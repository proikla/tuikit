from enum import IntEnum
import os


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


def color(color: int = 0) -> str:
    '''Returns \033[0;{color}m '''
    return f'\033[0;{color}m'


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

    def __init__(self, name: str = 'Untitled UI', show_name: bool = True, show_current_page: bool = True, show_current_page_name: bool = True):
        self.pages: list[UI._Page] = []
        self.current_page: UI._Page = None
        self.name: str = name
        self.current_page_index: int = 0

        self.do_show_name: bool = show_name
        self.do_show_current_page_idx: bool = show_current_page
        self.do_show_current_page_name: bool = show_current_page_name
        self.header: str = self.update_header()

    def update_header(self) -> str:
        """
        Returns menu header.
        Header looks like this:

        P: CURRENT_PAGE_NAME
        menu_name 4/4
        ...

        """
        self.header = f" P: {self.current_page.label + '\n' if self.current_page and self.do_show_current_page_name else ''} {self.name + ' ' if self.do_show_name else ''}{self.current_page_index + 1 if self.do_show_current_page_idx else ''}/{len(self.pages)}\n"
        return self.header

    def render(self, page: '_Page' = None):
        '''print all elements in the provided page'''
        if not page:
            page = self.current_page

        print(self.update_header(), flush=True)
        for idx, element in enumerate(page.elements):
            print(
                f"{color(element.color)}{idx+1:2}: {element.label} {color()}", flush=True)

    def set_page(self, page: '_Page') -> None:
        if page in self.pages:
            self.current_page = page
            self.current_page_index = self.pages.index(page)

    def set_page_to_index(self, idx: int) -> None:
        if idx < len(self.pages) and idx >= 0 and self.current_page_index != idx:
            self.current_page = self.pages[idx]
            self.current_page_index = idx

    def ask_input(self) -> int:
        """
        Prompts number input, return it. \n
        If 'a' or 'd' key is pressed, switch page to left or right accordingly, return -1. \n
        """
        print('>>> ', end='', flush=True)

        key = get_keypress()

        if key in ['\r', '\x08']:
            return -1

        if key == 'd':
            self.set_page_to_index(self.current_page_index+1)
            return -1
        if key == 'a':
            self.set_page_to_index(self.current_page_index-1)
            return -1

        print(key, end='', flush=True)
        user_input = key + input()

        if user_input.isnumeric() and int(user_input) <= len(self.current_page.elements):
            user_input = int(user_input)
            index = user_input-1
            if self.current_page.elements[index].command:
                self.current_page.elements[index]()

            return user_input
        return -1

    def loop(self, stop: bool = False) -> None:
        if not self.pages:
            self.current_page = self.add_page()

        while True:
            if stop:
                skip = True

            self.render(self.current_page)

            usr = self.ask_input()

            if usr >= 0:
                if self.current_page.elements[usr-1].command:
                    self.current_page.elements[usr-1]()
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
            self.elements.append(element)
            return element

        class _Element:
            def __call__(self) -> None:
                #  determine argcount.
                argcount = self.command.__code__.co_argcount
                # fix
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
                self.params: tuple | any = params
                self.color: int = color
