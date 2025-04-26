import os
import platform

REGULAR = 0
BOLD = 1
DIMMED = 2
ITALIC = 3
UNDERSCORE_INTERSECT = 4
FLASHING = 5
STRIKETHROUGH = 9
DOUBLE_UNDERSCORE_INTERSECT = 21
UNDERSCORE = 53
SELECTED = 7

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
    '''Returns \033[0;{mode}m '''
    return f'\033[0;{color}m'


def cls():
    '''clears console depending on the platform'''
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")


class UI:

    def __init__(self, name='Untitled UI'):
        self.pages: list[UI._Page] = []
        self.current_page: UI._Page = None
        self.name: str = name
        self.current_page_index: int = 0

    def render(self, page: '_Page'):
        '''print all elements in the provided page'''
        for idx, element in enumerate(page.elements):
            print(
                f"{color(element.color)}{idx+1:2}: {element.label} {color()}")

    def set_page(self, page: '_Page'):
        if page in self.pages:
            self.current_page = page
            self.current_page_index = self.pages.index(page)

    def set_page_to_index(self, idx: int) -> None:
        if idx < len(self.pages) and idx >= 0:
            self.current_page = self.pages[idx]
            self.current_page_index = idx

    def loop(self, stop: bool = False):
        if not self.pages:
            self.current_page = self.add_page()

        while True:
            if stop:
                skip = True

            self.render(self.current_page)

            user_input = input("Input: ")

            if user_input.lower() == 'd':
                self.set_page_to_index(self.current_page_index+1)
            if user_input.lower() == 'a':
                self.set_page_to_index(self.current_page_index-1)

            if user_input.isnumeric() and int(user_input) <= len(self.current_page.elements):
                user_input = int(user_input)
                index = user_input-1
                if self.current_page.elements[index].command:
                    self.current_page.elements[index]()
                    skip = False

            if stop and not skip:
                input()

            # Todo: use \r instead
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

        def add_element(self, name, command=None, params: list = None, color=0) -> '_Element':
            element = self._Element(name, command, params, color)
            self.elements.append(element)
            return element

        class _Element:
            def __call__(self):
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
                self.label = label
                self.command: callable = command
                self.params = params
                self.color = color
