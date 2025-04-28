from enum import IntEnum
import os
from typing import Iterable, Union


class Style(IntEnum):
    """Styles to use with color()"""
    REGULAR = 0
    BOLD = 1
    DIMMED = 2
    ITALIC = 3
    UNDERSCORE_INTERSECT = 4
    FLASHING = 5
    STRIKETHROUGH = 9
    DOUBLE_UNDERSCORE_INTERSECT = 21
    UNDERSCORE = 53
    INVERTED = 7

    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    PURPLE = 35
    LIGHTBLUE = 36

    BG_GRAY = 100
    BG_RED = 101
    BG_GREEN = 102
    BG_YELLOW = 103
    BG_CYAN = 104
    BG_PURPLE = 105
    BG_TURQUOISE = 106
    BG_WHITE = 107

    GRAY_BRIGHT = 90
    RED_BRIGHT = 91
    GREEN_BRIGHT = 92
    YELLOW_BRIGHT = 93
    BLUE_BRIGHT = 94
    PURPLE_BRIGHT = 95
    TURQUOISE = 96
    WHITE_BRIGHT = 97

    def __or__(self, other: "Style|CombinedStyle") -> "CombinedStyle":
        # Style.X | Style.Y or Style.X | CombinedStyle(...)
        if isinstance(other, Style):
            return CombinedStyle({self, other})
        if isinstance(other, CombinedStyle):
            return CombinedStyle({self, *other._styles})
        return NotImplemented

    def __ror__(self, other: "CombinedStyle") -> "CombinedStyle":
        # CombinedStyle | Style
        if isinstance(other, CombinedStyle):
            return CombinedStyle({*other._styles, self})
        return NotImplemented


class CombinedStyle:
    """Helper to hold a set of Style members."""
    __slots__ = ("_styles",)

    def __init__(self, styles: Iterable[Style]):
        # drop duplicates automatically via a frozenset
        self._styles = frozenset(styles)

    def __or__(self, other: Style) -> "CombinedStyle":
        if not isinstance(other, Style):
            return NotImplemented
        return CombinedStyle({*self._styles, other})

    def __iter__(self):
        return iter(self._styles)


def color(style: Union[Style, CombinedStyle] = None) -> str:
    """
    Get ANSI escape sequences according to the given style(s).

    Parameters
    ----------
    style : Style or tuple of Style
        One or more `Style` enum members (e.g. `Style.RED`, or `Style.BOLD | Style.UNDERLINE`)
        specifying ANSI codes to apply. Use `Style.REGULAR` (or no style) to return the unmodified text.

    Returns
    -------
    str
        The original `text` wrapped in the appropriate ANSI escape codes, e.g.
        `"\033[31;1mHello\033[0m"` for `Style.RED | Style.BOLD`.

    Example
    --------
    >>> color(Style.YELLOW | Style.BOLD)
    '\\033[33;1m\\033[0m'
    >>> color()
    '\\033[0m'
    """
    if not style:
        return "\033[0m"

    if isinstance(style, Style):
        codes = [] if style is Style.REGULAR else [str(style.value)]
    else:  # CombinedStyle
        codes = [str(s.value) for s in style if s is not Style.REGULAR]

    return f"\033[{';'.join(codes)}m"


def cls():
    '''clears console depending on the platform'''
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


# cross platfrom way to get keypress
if os.name == 'nt':
    import msvcrt

    def get_keypress():
        return msvcrt.getch().decode('utf-8')
else:
    import sys
    import termios
    import tty

    def get_keypress():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class UI:

    def __init__(self, name: str = 'Untitled UI', header: str | None = None, show_name: bool = True, show_current_page: bool = True, show_current_page_name: bool = True):
        self.pages: list[UI._Page] = []
        self.name: str = name
        self._current_page = None
        self._current_page_index = -1

        self.show_name: bool = show_name
        self.show_current_page_idx: bool = show_current_page
        self.show_current_page_name: bool = show_current_page_name

        if header:
            self.header = header
            self._has_custom_header = True
        else:
            self.header: str = self.make_header()
            self._has_custom_header = False

    def append_element(self, name: str, command=None, params=None, color=0) -> 'UI._Page._Element':
        """
        Append new element to the last page. If no pages - create Untitled page.
        Returns:
            'UI._Page._Element':

        >>> from tuikit import UI
        >>> ui = UI()
        >>> ui.add_page()
        ''
        """
        if not self.pages:
            page = self.add_page()
        else:
            page = self.pages[len(self.pages)-1]
        element = page._Element(name, command, params, color)
        element._parent_page = page
        page.elements.append(element)
        return page._ElementProxy(element)

    def make_header(self) -> str:
        """
        Returns:
            str: menu header.

        >>> make_header()
        "P: CURRENT_PAGE_NAME\\nmenu_name 4/4"
        """
        self.header = f" P: {self.current_page.label + '\n' if self.current_page and self.show_current_page_name else ''} {self.name + ' ' if self.show_name else ''}{self.current_page_index + 1 if self.show_current_page_idx else ''}/{len(self.pages)}\n"
        return self.header

    def render(self, page: '_Page' = None):
        '''print all elements in the provided page'''
        if not page:
            page = self.current_page

        if self._has_custom_header:
            header = self.header
        else:
            header = self.make_header()

        print(header, flush=True)
        for idx, element in enumerate(page.elements):
            print(
                f"{color(element.color)}{idx+1:2}: {element.label} {color()}", flush=True)

    @property
    def current_page(self):
        return self._current_page

    @current_page.setter
    def current_page(self, page: '_Page'):
        if page in self.pages:
            self._current_page = page
            self._current_page_index = self.pages.index(page)

    @property
    def current_page_index(self):
        return self._current_page_index

    @current_page_index.setter
    def current_page_index(self, idx: int):
        if 0 <= idx < len(self.pages):
            self._current_page_index = idx
            self._current_page = self.pages[idx]

    def ask_input(self, change_page_on_keypress=True, cursor='>>>') -> int:
        """
        Prompts number input, return it. \n
        If 'a' or 'd' key is pressed, switch page to left or right accordingly, return None. \n
        """
        print(cursor, end='', flush=True)

        key = get_keypress() if change_page_on_keypress else ''

        if key in ['\r', '\x08']:
            return None

        if key == 'd':
            self.current_page_index += 1
            return None
        if key == 'a':
            self.current_page_index -= 1
            return None

        print(key, end='', flush=True)
        user_input = key + input()
        
        if user_input.isnumeric() and int(user_input) <= len(self.current_page.elements):
            user_input = int(user_input)
            index = user_input-1
            if self.current_page.elements[index].command:
                self.current_page.elements[index]()

            return user_input
        return None

    def loop(self, stop: bool = False) -> None:
        if not self.pages:
            self.current_page = self.add_page()

        while True:
            if stop:
                skip = True

            self.render(self.current_page)

            usr = self.ask_input()

            if usr >= 0 and self.current_page.elements[usr-1].command:
                skip = False

                if stop and not skip:
                    input()

            cls()

    def add_page(self, label: str = f'Untitled page') -> '_Page':
        page = self._Page(label)
        self.pages.append(page)

        if len(self.pages) == 1:
            self.current_page = page

        return page

    class _Page:

        def __init__(self, label: str = 'Untitled page'):
            self.label = label
            self.elements: list[UI._Page._Element] = []

        def add_element(self, name: str, command=None, params=None, color=0) -> '_Element':
            element = self._Element(name, command, params, color)
            element._parent_page = self  # link back Page
            self.elements.append(element)
            return self._ElementProxy(element)  # return a proxy

        class _Element:
            def __call__(self) -> None:
                #  determine argcount.
                argcount = self.command.__code__.co_argcount

                # ? fix
                if argcount > 0 and self.command.__code__.co_varnames[0] == 'self':
                    argcount -= 1

                # if there is no arguments
                if argcount == 0 and not type(self.params) is type(tuple()):
                    self.command()

                elif argcount == 1:
                    self.command(self.params)

                # in case argument unpack is needed
                else:
                    self.command(*self.params)

            def __init__(self, label, command, params, color=0):
                self.label: str = label
                self.command: function = command
                self.params: tuple = params
                self.color: int = color
                self._parent_page = None

        class _ElementProxy:
            def __init__(self, element):
                self._element = element

            def __getattr__(self, item):
                try:
                    return getattr(self._element, item)
                except AttributeError:
                    # fall back to parent page
                    attr = getattr(self._element._parent_page, item)
                    if callable(attr):
                        return attr.__get__(self._element._parent_page)
                    return attr
