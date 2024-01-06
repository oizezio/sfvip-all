import tkinter as tk
from typing import Any, Callable, NamedTuple, Optional, Sequence

from translations.loc import LOC

from ...mitm.epg.update import EPGProgress, EPGstatus
from ..app_info import AppInfo
from .fx import Fade
from .sticky import Offset, StickyWindow
from .style import Style
from .widgets import (
    Border,
    Button,
    CheckBox,
    HorizontalScale,
    ListView,
    get_border,
    set_vscrollbar_style,
)


class Info(NamedTuple):
    name: str
    proxy: str
    upstream: str

    @property
    def is_valid(self) -> bool:
        return bool(self.proxy)


class _InfoTheme:
    pad = 2
    button_pad = 7
    bg_interact = "#1F1F1F"
    bg_headers = "#242424"
    bg_rows = "#2A2A2A"
    separator = "#303030"
    border = Border(bg="#808080", size=1, relief="")
    button = dict(bg="#1F1E1D", mouseover="#3F3F41", border=Border(bg="white", size=0.75, relief="groove"))
    listview = dict(bg_headers=bg_headers, bg_rows=bg_rows, bg_separator=separator)
    listview_scrollbar = dict(bg=bg_rows, slider="white", active_slider="grey")


class _InfoStyle:
    stl = Style().font("Calibri").font_size(12).max_width(30)
    arrow = stl("➜").color("#555555").bigger(5)
    upstream = stl.copy().color("#A0A0A0")
    proxy = stl.copy().white
    name = upstream.copy()
    blank = stl("")
    app_warn = stl.copy().smaller(2).no_truncate
    app = stl.copy().smaller(2)


def _get_infos_headers(app_name: str) -> Sequence[Style]:
    return (
        _InfoStyle.name(LOC.User).bigger(2).bold,
        _InfoStyle.blank,
        _InfoStyle.proxy(LOC.Proxy % app_name).bigger(2).bold,
        _InfoStyle.blank,
        _InfoStyle.upstream(LOC.UserProxy).bigger(2).bold,
    )


def _get_row(info: Info) -> Sequence[Style]:
    return (
        _InfoStyle.name(info.name) if info.name else _InfoStyle.name("-").grey,
        _InfoStyle.arrow if info.name else _InfoStyle.blank,
        _InfoStyle.proxy(info.proxy) if info.proxy else _InfoStyle.stl(LOC.NoProxy).red,
        _InfoStyle.arrow if info.upstream else _InfoStyle.blank,
        _InfoStyle.upstream(info.upstream) if info.upstream else _InfoStyle.stl("-").grey,
    )


def _get_relaunch_button() -> Style:
    return _InfoStyle.stl(LOC.RestartFixProxy).no_truncate.white


def _get_app_version(app_info: AppInfo) -> Style:
    return _InfoStyle.app(f"{app_info.name} v{app_info.version} {app_info.bitness}").grey


def _get_app_warn(app_info: AppInfo) -> Style:
    if app_info.bitness != app_info.os_bitness:
        warn = LOC.ShouldUseVersion % app_info.os_bitness
        return _InfoStyle.app_warn(warn).red
    warn = LOC.SearchWholeCatalog
    return _InfoStyle.app_warn(warn).lime_green


def _get_app_button_text(action: Optional[str] = None, version: Optional[str] = None) -> Style:
    return _InfoStyle.app(f"{action or ''} v{version or ''}").no_truncate.white


def _get_app_auto_update() -> Style:
    return _InfoStyle.app(LOC.CheckUpdate).grey


def _get_libmpv_version(version: Optional[str] = None) -> Style:
    version = version if version else LOC.UnknownVersion
    return _InfoStyle.app(f"Libmpv {version}").grey


def _get_libmpv_auto_update() -> Style:
    return _InfoStyle.app(LOC.CheckUpdate).grey


def _get_libmpv_button_text(action: Optional[str] = None, version: Optional[str] = None) -> Style:
    return _InfoStyle.app(f"{action or ''} {version or ''}").no_truncate.white


def _get_player_button_text(action: Optional[str] = None, version: Optional[str] = None) -> Style:
    return _InfoStyle.app(f"{action or ''} v{version or ''}").no_truncate.white


def _get_player_version(version: Optional[str] = None) -> Style:
    version = version if version else LOC.UnknownVersion
    return _InfoStyle.app(f"Sfvip Player v{version}").grey


def _get_player_auto_update() -> Style:
    return _InfoStyle.app(LOC.CheckUpdate).grey


def _are_infos_valid(infos: Sequence[Info]) -> bool:
    return all(info.is_valid for info in infos)


def _epg() -> Style:
    return _InfoStyle.app(LOC.EpgUrl).grey


def _epg_url() -> Style:
    return _InfoStyle.app("").smaller(2).no_truncate.grey


def _epg_confidence_label() -> Style:
    return _InfoStyle.app(LOC.EpgConfidence).no_truncate.grey


def _epg_confidence(confidence: int) -> Style:
    return _InfoStyle.app(f"{confidence}%").no_truncate.grey


def _epg_status_styles(progress: str) -> dict[EPGstatus | None, Style]:
    return {
        EPGstatus.LOADING: _InfoStyle.app(f"{LOC.Loading}{progress}").grey,
        EPGstatus.PROCESSING: _InfoStyle.app(f"{LOC.Processing}{progress}").grey,
        EPGstatus.READY: _InfoStyle.app(LOC.Ready).lime_green,
        EPGstatus.FAILED: _InfoStyle.app(LOC.Failed).red,
        EPGstatus.NO_EPG: _InfoStyle.app(LOC.NoEpg).grey,
        EPGstatus.INVALID_URL: _InfoStyle.app(LOC.InvalidUrl).red,
    }


def _epg_status(epg_status: EPGProgress) -> Style:
    progress = "" if epg_status.progress is None else f" {epg_status.progress:.0%}"
    return _epg_status_styles(progress).get(epg_status.status, _InfoStyle.app("").grey)


class _ProxiesWindow(StickyWindow):
    """installed proxies infos"""

    _offset = Offset(regular=(-36, 36), maximized=(2, 35))
    _max_height = 400

    def __init__(self, app_info: AppInfo) -> None:
        border = get_border(_InfoTheme.border)
        super().__init__(InfosWindow._offset, **border, bg=_InfoTheme.bg_rows)
        self.attributes("-alpha", 0.0)
        self.maxsize(-1, InfosWindow._max_height)
        # create a frame for hovering detection
        self._frame = tk.Frame(self, bg=_InfoTheme.bg_rows)
        self._frame.pack(expand=True, fill=tk.BOTH)
        self._bind_mouse_hover(self._frame)
        self._fade = Fade(self)
        # widgets
        self._header_frame = tk.Frame(self._frame, bg=_InfoTheme.bg_headers)
        self._relaunch_button = Button(
            self._header_frame, **_InfoTheme.button, **_get_relaunch_button().to_tk, attached_to=self._header_frame
        )
        self._listview = ListView(self._frame, **_InfoTheme.listview, pad=_InfoTheme.pad)
        self._listview.set_headers(_get_infos_headers(app_info.name))
        set_vscrollbar_style(**_InfoTheme.listview_scrollbar)

    def _layout(self, row: int) -> None:
        button_pad = _InfoTheme.button_pad
        self._header_frame.grid(row=row, columnspan=3, sticky=tk.NSEW)
        self._header_frame.columnconfigure(0, weight=1)
        self._relaunch_button.grid(padx=button_pad, pady=button_pad, sticky=tk.NSEW)
        self._relaunch_button.grid_remove()
        row += 1
        self._listview.grid(row=row, columnspan=3, sticky=tk.NSEW)
        self._frame.rowconfigure(row, weight=1)

    def _set_button_action(self, button: Button, action: Optional[Callable[..., None]], *args: Any) -> None:
        if action:

            def _action(_) -> None:
                button.unbind("<Button-1>")
                button.grid_remove()
                # give time for the button feedback
                self.after(100, action, *args)
                self.geometry("")  # resize the window

            button.grid()
            button.bind("<Button-1>", _action)
        else:
            button.grid_remove()
        self.geometry("")  # resize the window

    def _bind_mouse_hover(self, widget: tk.Widget) -> None:
        def show(_) -> None:
            """keep showing only when already there to avoid showing again when fading out"""
            if self.attributes("-alpha") == 1.0:
                self.show()

        widget.bind("<Enter>", show, add="+")
        widget.bind("<Leave>", lambda _: self.hide(), add="+")

    def set(self, infos: Sequence[Info], player_relaunch: Optional[Callable[[int], None]]) -> bool:
        rows = [_get_row(info) for info in infos]
        if not rows:
            rows = [_get_row(Info("", "-", ""))]
        self._listview.set_rows(rows)
        # add relaunch if not valid
        valid = _are_infos_valid(infos)
        relaunch = player_relaunch if not valid and player_relaunch else None
        # instant relaunch if needed
        self._set_button_action(self._relaunch_button, relaunch, 0)
        return valid

    def show(self) -> None:
        self._fade.fade(fade_duration_ms=250, out=False)

    def hide(self) -> None:
        self._fade.fade(fade_duration_ms=250, out=True, wait_ms=100)


class InfosWindow(_ProxiesWindow):
    # pylint: disable=too-many-instance-attributes, too-many-statements, too-many-locals
    def __init__(self, app_info: AppInfo) -> None:
        super().__init__(app_info)
        pad = _InfoTheme.pad
        button_pad = _InfoTheme.button_pad
        frame = self._frame
        # widgets
        header_frame = tk.Frame(frame, bg=_InfoTheme.bg_headers)
        app_warn_label = tk.Label(header_frame, bg=_InfoTheme.bg_headers, **_get_app_warn(app_info).to_tk)
        separator = tk.Frame(frame, bg=_InfoTheme.separator)
        self._app_button = Button(frame, **_InfoTheme.button)  # type: ignore
        app_version = tk.Label(frame, bg=_InfoTheme.bg_rows, **_get_app_version(app_info).to_tk)
        self._app_update = CheckBox(frame, bg=_InfoTheme.bg_rows, **_get_app_auto_update().to_tk)
        separator2 = tk.Frame(frame, bg=_InfoTheme.separator)
        self._player_version = tk.Label(frame, bg=_InfoTheme.bg_rows, **_get_player_version().to_tk)
        self._player_update = CheckBox(frame, bg=_InfoTheme.bg_rows, **_get_player_auto_update().to_tk)
        self._player_button = Button(frame, **_InfoTheme.button)  # type: ignore
        separator3 = tk.Frame(frame, bg=_InfoTheme.separator)
        self._libmpv_version = tk.Label(frame, bg=_InfoTheme.bg_rows, **_get_libmpv_version().to_tk)
        self._libmpv_update = CheckBox(frame, bg=_InfoTheme.bg_rows, **_get_libmpv_auto_update().to_tk)
        self._libmpv_button = Button(frame, **_InfoTheme.button)  # type: ignore
        separator4 = tk.Frame(frame, bg=_InfoTheme.separator)
        epg_frame = tk.Frame(frame, bg=_InfoTheme.bg_rows)
        epg_label = tk.Label(epg_frame, bg=_InfoTheme.bg_rows, **_epg().to_tk)
        self._epg_url = tk.Entry(
            epg_frame,
            bg=_InfoTheme.bg_interact,
            disabledbackground=_InfoTheme.bg_rows,
            **_epg_url().to_tk,
            insertbackground="grey",
            borderwidth=0,
            highlightthickness=0,
            width=50,
        )
        self._epg_status = tk.Label(epg_frame, bg=_InfoTheme.bg_rows)
        epg_confidence_frame = tk.Frame(frame, bg=_InfoTheme.bg_rows)
        epg_confidence_label = tk.Label(
            epg_confidence_frame, bg=_InfoTheme.bg_rows, **_epg_confidence_label().to_tk
        )
        self._epg_confidence = tk.Label(epg_confidence_frame, bg=_InfoTheme.bg_rows, width=4, anchor=tk.E)
        self._epg_confidence_slider = HorizontalScale(
            epg_confidence_frame,
            from_=0,
            to=100,
            bg=_InfoTheme.bg_rows,
            trough_color=_InfoTheme.bg_interact,
            trough_height=3,
            slider_width=7,
            slider_height=10,
            slider_color="grey",
            slider_color_active="white",
        )
        separator5 = tk.Frame(frame, bg=_InfoTheme.separator)
        # layout
        row = 0
        header_frame.grid(row=row, columnspan=3, padx=pad, sticky=tk.NSEW)
        app_warn_label.pack(expand=True, anchor=tk.W)
        row += 1
        separator.grid(row=row, columnspan=3, sticky=tk.EW)
        row += 1
        app_version.grid(row=row, padx=pad, sticky=tk.W)
        self._app_update.grid(row=row, column=1, padx=pad, sticky=tk.EW)
        self._app_button.grid(row=row, column=2, padx=button_pad, pady=button_pad, sticky=tk.EW)
        self._app_button.grid_remove()
        row += 1
        separator2.grid(row=row, columnspan=3, sticky=tk.EW)
        row += 1
        self._player_version.grid(row=row, column=0, padx=pad, sticky=tk.W)
        self._player_update.grid(row=row, column=1, padx=pad, sticky=tk.EW)
        self._player_button.grid(row=row, column=2, padx=button_pad, pady=button_pad, sticky=tk.EW)
        self._player_button.grid_remove()
        row += 1
        separator3.grid(row=row, columnspan=3, sticky=tk.EW)
        row += 1
        self._libmpv_version.grid(row=row, column=0, padx=pad, sticky=tk.W)
        self._libmpv_update.grid(row=row, column=1, padx=pad, sticky=tk.EW)
        self._libmpv_button.grid(row=row, column=2, padx=button_pad, pady=button_pad, sticky=tk.EW)
        self._libmpv_button.grid_remove()
        row += 1
        separator4.grid(row=row, columnspan=3, sticky=tk.EW)
        row += 1
        epg_frame.grid(row=row, columnspan=3, sticky=tk.NSEW)
        epg_label.pack(padx=pad, side=tk.LEFT)
        self._epg_url.pack(pady=pad * 2, side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._epg_status.pack(padx=pad, side=tk.LEFT)
        row += 1
        epg_confidence_frame.grid(row=row, columnspan=3, sticky=tk.NSEW)
        epg_confidence_label.pack(padx=pad, side=tk.LEFT)
        self._epg_confidence_slider.pack(pady=pad, side=tk.LEFT, fill=tk.X, expand=True)
        self._epg_confidence.pack(padx=pad, side=tk.LEFT)
        row += 1
        separator5.grid(row=row, columnspan=3, sticky=tk.EW)
        row += 1
        super()._layout(row=row)
        frame.columnconfigure(2, weight=1)

    def set_epg_url_update(self, epg_url: Optional[str], callback: Callable[[str], None]) -> None:
        self._epg_url.delete(0, tk.END)
        if epg_url:
            self._epg_url.insert(0, epg_url)
        self._epg_url.bind("<Return>", lambda _: callback(self._epg_url.get()))
        self._epg_url.bind("<FocusOut>", lambda _: callback(self._epg_url.get()))

    def set_epg_status(self, epg_status: EPGProgress) -> None:
        self._epg_url.config(state=tk.DISABLED if epg_status.status is EPGstatus.LOADING else tk.NORMAL)
        self._epg_status.config(**_epg_status(epg_status).to_tk)

    def set_epg_confidence_update(self, confidence: int, callback: Callable[[int], None]) -> None:
        def _callback(event: tk.Event) -> None:
            try:
                confidence = round(self._epg_confidence_slider.get())
                self._epg_confidence.config(**_epg_confidence(confidence).to_tk)
                if event.type == tk.EventType.ButtonRelease:
                    callback(confidence)
            except ValueError:
                pass

        confidence = max(0, min(confidence, 100))
        self._epg_confidence_slider.set(confidence)
        self._epg_confidence.config(**_epg_confidence(confidence).to_tk)
        self._epg_confidence_slider.bind("<ButtonRelease-1>", _callback)
        self._epg_confidence_slider.bind("<B1-Motion>", _callback)

    def set_app_update(
        self,
        action_name: Optional[str],
        action: Optional[Callable[[], None]],
        version: Optional[str],
    ) -> None:
        self._app_button.config(**_get_app_button_text(action_name, version).to_tk)
        self._set_button_action(self._app_button, action)

    def set_app_auto_update(self, is_checked: bool, callback: Callable[[bool], None]) -> None:
        self._app_update.set_callback(is_checked, callback)

    def set_libmpv_version(self, version: Optional[str]) -> None:
        self._libmpv_version.config(**_get_libmpv_version(version).to_tk)
        self.geometry("")  # resize the window

    def set_libmpv_update(
        self,
        action_name: Optional[str],
        action: Optional[Callable[[], None]],
        version: Optional[str],
    ) -> None:
        self._libmpv_button.config(**_get_libmpv_button_text(action_name, version).to_tk)
        self._set_button_action(self._libmpv_button, action)

    def set_libmpv_auto_update(self, is_checked: bool, callback: Callable[[bool], None]) -> None:
        self._libmpv_update.set_callback(is_checked, callback)

    def set_player_version(self, version: Optional[str]) -> None:
        self._player_version.config(**_get_player_version(version).to_tk)
        self.geometry("")  # resize the window

    def set_player_update(
        self,
        action_name: Optional[str],
        action: Optional[Callable[[], None]],
        version: Optional[str],
    ) -> None:
        self._player_button.config(**_get_player_button_text(action_name, version).to_tk)
        self._set_button_action(self._player_button, action)

    def set_player_auto_update(self, is_checked: bool, callback: Callable[[bool], None]) -> None:
        self._player_update.set_callback(is_checked, callback)
