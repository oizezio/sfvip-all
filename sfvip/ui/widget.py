import tkinter as tk
from typing import Collection

from pyparsing import Sequence

from .style import _Style


class _AutoScrollbar(tk.Scrollbar):
    def set(self, first, last):
        if float(first) <= 0.0 and float(last) >= 1.0:
            self.grid_remove()
        else:
            self.grid()
        super().set(first, last)


class _VscrollCanvas(tk.Canvas):  # pylint: disable=too-many-ancestors
    """
    Canvas with an automatic vertical scrollbar
    use _VAutoScrollableCanvas.frame to populate it
    """

    def __init__(self, master: tk.BaseWidget, **kwargs) -> None:
        super().__init__(master, bd=0, highlightthickness=0, **kwargs)  # w/o border
        # set the vertical scrollbar
        vscrollbar = _AutoScrollbar(master, orient="vertical")
        self.config(yscrollcommand=vscrollbar.set, yscrollincrement="2")
        vscrollbar.config(command=self.yview)
        self.scrollbar = vscrollbar
        # position everything
        vscrollbar.grid(row=0, column=1, sticky=tk.NS)
        self.grid(row=0, column=0, sticky=tk.NSEW)
        # Making the canvas expandable
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        # creating the frame attached to self
        self.frame = tk.Frame(self, bg=self["bg"])
        self.create_window(0, 0, anchor=tk.NW, window=self.frame)
        # set the scroll region when the frame content changes
        self.frame.bind("<Configure>", self._on_configure)
        # bind the mousewheel
        self.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_configure(self, _):
        w, h = self.frame.winfo_reqwidth(), self.frame.winfo_reqheight()
        self.config(scrollregion=(0, 0, w, h), width=w, height=h)

    def _on_mousewheel(self, event):
        self.yview_scroll(int(-1 * (event.delta / 12)), "units")


class _Button(tk.Button):
    """
    button with a colored border
    with a mouseover color
    """

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        master: tk.BaseWidget,
        bg: str,
        mouseover: str,
        bd_color: str,
        bd_width: float,
        bd_relief: str,
        **kwargs
    ) -> None:
        # create a frame for the border, note: do not pack
        border = dict(highlightbackground=bd_color, highlightcolor=bd_color, bd=bd_width, relief=bd_relief)
        self._frame = tk.Frame(master, bg=bg, **border)
        active = dict(activebackground=bg, activeforeground=kwargs.get("fg", "white"))
        # create the button
        super().__init__(self._frame, bg=bg, bd=0, **active, **kwargs)
        super().pack(fill="both", expand=True)
        # handle mouseover
        self.bind("<Enter>", lambda _: self.config(bg=mouseover), add="+")
        self.bind("<Leave>", lambda _: self.config(bg=bg), add="+")

    def grid(self, **kwargs) -> None:
        self._frame.grid(**kwargs)

    def grid_remove(self) -> None:
        self._frame.grid_remove()

    def pack(self, **kwargs) -> None:
        self._frame.pack(**kwargs)


class _ListView(tk.Frame):
    """List view with styled content and auto scroll"""

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        master: tk.BaseWidget,
        bg_headers: str,
        bg_row: str,
        bg_separator: str,
        pad: int,
    ) -> None:
        super().__init__(master)
        # headers
        self._frame_headers = tk.Frame(self, bg=bg_headers)
        self._frame_headers.pack(fill="both", expand=True)
        # headers separator
        sep = tk.Frame(self, bg=bg_separator)
        sep.pack(fill="both", expand=True)
        # rows
        frame_list = tk.Frame(self)
        canvas = _VscrollCanvas(frame_list, bg=bg_separator)
        self._frame_list = canvas.frame
        frame_list.pack(fill="both", expand=True)

        self._bg_headers = bg_headers
        self._bg_row = bg_row
        self._bg_separator = bg_separator
        self._pad = pad

    @staticmethod
    def _clear(what: tk.BaseWidget):
        for widget in what.winfo_children():
            widget.destroy()

    def set(self, headers: Collection[_Style], rows: Sequence[Collection[_Style]]) -> None:
        # clear the frame
        self._clear(self._frame_headers)
        self._clear(self._frame_list)
        # populate
        pad = self._pad
        n_column = len(headers)
        widths = [0] * n_column
        # headers
        for column, text in enumerate(headers):
            label = tk.Label(self._frame_headers, bg=self._bg_headers, **text.to_tk)
            label.grid(row=0, column=column, ipadx=pad, ipady=pad, sticky=tk.NSEW)
            widths[column] = max(label.winfo_reqwidth() + pad * 2, widths[column])
        # rows
        for row, row_content in enumerate(rows):
            assert len(row_content) == n_column
            for column, text in enumerate(row_content):
                label = tk.Label(self._frame_list, bg=self._bg_row, **text.to_tk)
                label.grid(row=row * 2, column=column, ipadx=pad, ipady=pad, sticky=tk.NSEW)
                widths[column] = max(label.winfo_reqwidth() + pad * 2, widths[column])
                # row separator
                if row != len(rows) - 1:
                    sep = tk.Frame(self._frame_list, bg=self._bg_separator)
                    sep.grid(row=row * 2 + 1, column=0, columnspan=n_column, sticky=tk.EW)
        # sync both grids
        for i in range(n_column):
            self._frame_headers.columnconfigure(i, minsize=widths[i])
            self._frame_list.columnconfigure(i, minsize=widths[i])
