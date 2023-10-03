import tkinter as tk
from pathlib import Path
from tkinter import filedialog
from typing import Callable, Optional, Sequence

from .infos import AppInfo, Info, _InfosWindow
from .logo import _LogoWindow, _PulseReason
from .splash import _SplashWindow
from .thread import ThreadUI
from .window import AskWindow, MessageWindow, _Window


class UI(tk.Tk):
    """basic UI with a tk mainloop, the app has to run in a thread"""

    def __init__(self, app_info: AppInfo, splash_path: Path, logo_path: Path) -> None:
        super().__init__()
        self.withdraw()  # we rely on some _StickyWindow instead
        self._splash_img = tk.PhotoImage(file=splash_path)  # keep a reference for tk
        self.wm_iconphoto(True, self._splash_img)
        self.splash = _SplashWindow(self._splash_img)
        self._infos = _InfosWindow(app_info)
        self._logo = _LogoWindow(logo_path, self._infos)
        _Window.set_logo(logo_path)
        self._title = f"{app_info.name} v{app_info.version} {app_info.bitness}"
        self._has_quit = False

    def quit(self) -> None:
        if not self._has_quit:
            self._has_quit = True
            _Window.quit_all()
            ThreadUI.quit()
            super().quit()

    def run_in_thread(self, target: Callable[[], None], *exceptions: type[Exception]) -> None:
        ThreadUI(self, *exceptions).start(target)

    def set_infos(self, infos: Sequence[Info], player_relaunch: Optional[Callable[[int], None]] = None) -> None:
        ok = self._infos.set(infos, player_relaunch)
        self._logo.set_pulse(ok=ok, reason=_PulseReason.RESTART_FOR_PROXIES)

    def set_app_auto_update(self, is_checked: bool, callback: Callable[[bool], None]) -> None:
        self._infos.set_app_auto_update(is_checked, callback)

    def set_app_updating(self) -> None:
        self._logo.set_pulse(ok=True, reason=_PulseReason.UPDATE_APP)

    def set_app_update(
        self,
        action_name: Optional[str] = None,
        action: Optional[Callable[[], None]] = None,
        version: Optional[str] = None,
    ) -> None:
        self._infos.set_app_update(action_name, action, version)
        self._logo.set_pulse(ok=action is None, reason=_PulseReason.UPDATE_APP)

    def set_libmpv_auto_update(self, is_checked: bool, callback: Callable[[bool], None]) -> None:
        self._infos.set_libmpv_auto_update(is_checked, callback)

    def set_libmpv_updating(self) -> None:
        self._logo.set_pulse(ok=True, reason=_PulseReason.UPDATE_LIBMPV)

    def set_libmpv_update(
        self,
        action_name: Optional[str] = None,
        action: Optional[Callable[[], None]] = None,
        version: Optional[str] = None,
    ) -> None:
        self._infos.set_libmpv_update(action_name, action, version)
        self._logo.set_pulse(ok=action is None, reason=_PulseReason.UPDATE_LIBMPV)

    def set_libmpv_version(self, version: Optional[str]) -> None:
        self._infos.set_libmpv_version(version)

    def showinfo(self, message: str, force: bool = False) -> None:
        def _showinfo() -> bool:
            message_win.wait_window()
            return True

        message_win = MessageWindow(self._title, message, force=force)
        message_win.run_in_thread(_showinfo)

    def ask(self, message: str, ok: str, cancel: str) -> Optional[bool]:
        def _ask() -> Optional[bool]:
            ask_win.wait_window()
            return ask_win.ok

        ask_win = AskWindow(self._title, message, ok, cancel)
        return ask_win.run_in_thread(_ask)

    def find_file(self, name: str, pattern: str) -> str:
        title = f"{self._title}: Find {name}"
        return filedialog.askopenfilename(title=title, filetypes=[(name, pattern)])
