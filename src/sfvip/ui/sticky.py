import threading
import tkinter as tk
from typing import Any, NamedTuple, Optional, Self

from ...winapi import monitor


class Offset(NamedTuple):
    regular: tuple[int, int] = 0, 0
    maximized: Optional[tuple[int, int]] = None
    center: tuple[float, float] = 0, 0


infinity = float("inf")
offset_centered = (0.5, 0.5)


class Rect(NamedTuple):
    x: float = infinity
    y: float = infinity
    w: float = infinity
    h: float = infinity
    is_maximized: bool = False

    def valid(self) -> bool:
        return all(attr != infinity for attr in (self.x, self.y, self.w, self.h))

    def position(self, offset: Offset, w: int, h: int) -> Self:
        x_ratio, y_ratio = offset.center
        x, y = offset.maximized if (self.is_maximized and offset.maximized) else offset.regular
        return self.__class__(self.x + x + (self.w - w) * x_ratio, self.y + y + (self.h - h) * y_ratio, w, h)

    def to_geometry(self) -> str:
        return f"{self.w}x{self.h}+{self.x:.0f}+{self.y:.0f}"

    def is_middle_inside(self, rect: Self) -> bool:
        x, y = self.x + self.w * 0.5, self.y + self.h * 0.5
        return (rect.x <= x <= rect.x + rect.w) and (rect.y <= y <= rect.y + rect.h)


class WinState(NamedTuple):
    rect: Rect
    is_minimized: bool
    no_border: bool
    is_topmost: bool
    is_foreground: bool


class StickyWindow(tk.Toplevel):
    """follow position, hide & show when needed"""

    show_when_no_border = False

    def __init__(self, offset: Offset, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.withdraw()
        self.overrideredirect(True)
        self._offset = offset
        # prevent closing (alt-f4)
        self.protocol("WM_DELETE_WINDOW", lambda: None)
        StickyWindows.register(self)

    def change_position(self, rect: Rect) -> None:
        w, h = self.winfo_reqwidth(), self.winfo_reqheight()
        rect = rect.position(self._offset, w, h)
        self.geometry(rect.to_geometry())

    def bring_to_front(self, is_topmost: bool, is_foreground: bool) -> None:
        # TODO !!!!!!!!!!!!!!!!!!!!????????????
        if self.state() != "normal":
            self.deiconify()
        if is_foreground:
            if is_topmost:
                self.attributes("-topmost", True)
            else:
                self.attributes("-topmost", True)
                self.attributes("-topmost", False)


class StickyWindows:
    """pure class, handle on_state_changed on all StickyWindow"""

    _current_rect: Optional[Rect] = None
    _instances: list[StickyWindow] = []
    _lock = threading.Lock()

    @staticmethod
    def register(instance: StickyWindow) -> None:
        StickyWindows._instances.append(instance)

    @staticmethod
    def get_rect() -> Optional[Rect]:
        return StickyWindows._current_rect

    @staticmethod
    def change_position_all(rect: Rect, border: bool) -> None:
        for sticky in StickyWindows._instances:
            if border or sticky.show_when_no_border:
                sticky.change_position(rect)

    @staticmethod
    def bring_to_front_all(is_topmost: bool, is_foreground: bool, border: bool) -> None:
        for sticky in StickyWindows._instances:
            if border or sticky.show_when_no_border:
                sticky.bring_to_front(is_topmost, is_foreground)

    @staticmethod
    def withdraw_all() -> None:
        for sticky in StickyWindows._instances:
            sticky.withdraw()

    @staticmethod
    def withdraw_all_no_border() -> None:
        for sticky in StickyWindows._instances:
            if not sticky.show_when_no_border:
                sticky.withdraw()

    @staticmethod
    def on_state_changed(state: WinState) -> None:
        with StickyWindows._lock:  # sure to be sequential
            if state.is_minimized:
                StickyWindows.withdraw_all()
                return
            if state.no_border:
                StickyWindows.withdraw_all_no_border()
            if state.rect.valid():
                StickyWindows.bring_to_front_all(state.is_topmost, state.is_foreground, not state.no_border)
                if state.rect != StickyWindows._current_rect:
                    StickyWindows._current_rect = state.rect
                    StickyWindows.change_position_all(Maximized.fix(state.rect), not state.no_border)

    @staticmethod
    def update_position(win: StickyWindow) -> None:
        if rect := StickyWindows._current_rect:
            win.change_position(rect)


class Maximized:
    """maximized window stay in its screen"""

    _monitor_rects = tuple(Rect(*area.work_area, True) for area in monitor.monitors_areas())

    @staticmethod
    def fix(rect: Rect) -> Rect:
        if rect.is_maximized:
            # fix possible wrong zoomed coords
            for monitor_rect in Maximized._monitor_rects:
                if rect.is_middle_inside(monitor_rect):
                    return monitor_rect
        return rect
