from enum import IntEnum
import os
import sys
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
    '\\033[m'
    """
    if not style:
        return "\033[m"

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
        key = msvcrt.getch()

        # ctrl + c
        if key == b'\x03':
            raise KeyboardInterrupt

        if key == b'\x00' or key == b'\xe0':  # arrow keys
            key = msvcrt.getch()  # capture next byte
            if key == b'H':  # up arrow
                return 'up'
            elif key == b'P':  # down arrow
                return 'down'
            elif key == b'K':  # left arrow
                return 'left'
            elif key == b'M':  # right arrow
                return 'right'

            return None

        return key.decode('utf-8')
else:
    import termios
    import tty

    def get_keypress():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            key = sys.stdin.read(1)
            # arrow keys check
            if key == '\x1b':  # escape char
                seq = sys.stdin.read(2)  # read the next two characters
                if seq == '[A':
                    return 'up'
                elif seq == '[B':
                    return 'down'
                elif seq == '[D':
                    return 'left'
                elif seq == '[C':
                    return 'right'
            return key
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


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

    def delete_page(self, page):
        if page in self.pages:
            self.pages.remove(page)

        elif isinstance(page, str):
            for p in self.pages:
                if getattr(p, "name", None) == page:
                    self.delete_page(p)
                    break
            else:
                raise ValueError(f"Page with name '{page}' not found.")
        else:
            raise TypeError("page must be a Page instance or string name")

    def rename(self, to: str = "Untitled UI"):
        self.name = to

    def append_element(self, name: str, command=None, params=None, color=Style.REGULAR) -> 'UI._Page._Element':
        """
        Append new element to the last page. If no pages - create Untitled page.
        Returns:
            'UI._Page._Element':

        >>> from tuikit import UI
        >>> ui = UI()
        >>> ui.append_element()
        """
        if not self.pages:
            page = self.add_page()
        else:
            page = self.pages[len(self.pages)-1]
        element = page._Element(name, command, params, color)
        element._parent_page = page
        page.elements.append(element)
        return page._ElementProxy(element)

    def add_page(self, label: str = f'Untitled page', default_padding=0) -> '_Page':
        page = self._Page(label, default_padding)
        self.pages.append(page)

        if len(self.pages) == 1:
            self.current_page = page

        return page

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
        '''print header and all elements in the provided page'''

        if not page:
            page = self.current_page

        # Header rendering
        if self._has_custom_header:
            header = self.header
        else:
            header = self.make_header()
        print(header, flush=True)

        # Elements rendering
        for idx, element in enumerate(page.elements):
            index = f"{idx+1:2}: "

            # calculate padding
            if page.default_padding:
                padding = page.default_padding
            else:
                padding = element.get_padding(offset=-len(index))

            # change element's color if it is selected.
            if page.selected_element and element is page.selected_element:
                element_color = element.color | Style.INVERTED
            else:
                element_color = element.color

            print(
                f"{padding}{color(element_color)}{index}{element.label}{color()}", flush=True)

    def ask_input(self, change_page_on_keypress=True, cursor='>>> ') -> int:
        """
        Prompts number input, return it. \n
        If 'a' or 'd' key is pressed, switch page to left or right accordingly, return None. \n
        """
        print(cursor, end='', flush=True)

        key = get_keypress() if change_page_on_keypress else ''

        # backspace pressed
        if key == '\x08':
            return None

        # enter pressed
        if key == '\r':
            if self.current_page.selected_element:
                self.current_page.selected_element()
            return None

        current_page = self.current_page
        if key in ['a', 'd', 'w', 's', 'up', 'down', 'left', 'right']:
            if key == 'd' or key == 'right':
                self.pages[self.current_page_index].selected_element = None
                self.current_page_index += 1

            elif key == 'a' or key == 'left':
                self.pages[self.current_page_index].selected_element = None
                self.current_page_index -= 1

            elif key == 'w' or key == 'up':
                # if there's no selected element, make the last element selected.
                if not current_page.selected_element and current_page.elements:
                    current_page.selected_element = current_page.elements[-1]
                    return None

                # change selected element to the previous one.
                if current_page.elements.index(current_page.selected_element) > 0:
                    prev_element_index = current_page.elements.index(
                        current_page.selected_element)-1

                    current_page.selected_element = current_page.elements[prev_element_index]

            elif key == 's' or key == 'down':
                # if there's no selected element, make the first element selected.
                if current_page.elements and not current_page.selected_element:
                    current_page.selected_element = current_page.elements[0]
                    return None

                # change selected element to the next one.
                if current_page.elements.index(current_page.selected_element) < len(current_page.elements)-1:
                    next_element_index = current_page.elements.index(
                        current_page.selected_element)+1

                    current_page.selected_element = current_page.elements[next_element_index]

            return None

        print(key, end='', flush=True)
        user_input = key + input()

        # if an element is chosen by index, execute its command
        if user_input.isnumeric() and int(user_input) <= len(self.current_page.elements):
            user_input = int(user_input)
            index = user_input-1
            if self.current_page.elements[index].command:
                self.current_page.elements[index]()

            return user_input
        return None

    def loop(self, stop: bool = False) -> None:
        # page to render before user input
        this_page = self.current_page

        if not self.pages:
            self.current_page = self.add_page()

        while True:
            cls()

            if stop:
                skip = True

            self.render(self.current_page)

            usr = self.ask_input()

            # ?
            if usr and usr > 0 and this_page.elements[usr-1].command != None:
                skip = False
                if stop and not skip:
                    input()

    class _Page:

        def __init__(self, label: str = 'Untitled page', default_padding=0):
            self.label = label
            self.elements: list[UI._Page._Element] = []
            self.default_padding = ' ' * default_padding

            self._selected_element: 'UI._Page._Element' = None

        @property
        def selected_element(self):
            return self._selected_element

        @selected_element.setter
        def selected_element(self, element):
            if element is not None and element not in self.elements:
                return
            self._selected_element = element

        def rename(self, to: str = "Untitled page"):
            self.label = to

        def add_element(self, name: str, command=None, params=None, color=Style.REGULAR, alignment='left') -> '_Element':
            element = self._Element(name, command, params, color, alignment)
            element._parent_page = self  # link back Page
            self.elements.append(element)

            return self._ElementProxy(element)  # return a proxy

        def append_element(self, name: str, command=None, params=None, color=Style.REGULAR, alignment='left') -> '_Element':
            # when chaining
            return self.add_element(name, command, params, color, alignment)

        class _Element:
            def __call__(self) -> None:
                #  determine argcount.
                if not self.command:
                    return None

                argcount = self.command.__code__.co_argcount

                # ? fix
                if argcount > 0 and self.command.__code__.co_varnames[0] == 'self':
                    argcount -= 1

                # if there is no arguments
                if argcount == 0 and not isinstance(self.params, type):
                    self.command()

                elif argcount == 1:
                    self.command(self.params)

                # in case argument unpack is needed
                else:
                    self.command(*self.params)

            def __init__(self, label, command, params, color=Style.REGULAR, alignment='left'):
                self.label: str = label
                self.command: function = command
                self.params: tuple = params
                self.color = color
                self._parent_page = None
                self.alignment = alignment

            def rename(self, to: str = 'Untitled element') -> None:
                self.label = to

            def get_padding(self, offset=0):
                width, _ = os.get_terminal_size(sys.stdout.fileno())

                match self.alignment.lower():
                    case 'center':
                        return ' ' * (int(width/2) - int(len(self.label)/2) + offset)
                    case 'left':
                        return ' ' * offset
                    case 'right':
                        return ' ' * (width - len(self.label) + offset)

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
