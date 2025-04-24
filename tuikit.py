import os
import platform


def cls():
    '''clears console depending on the platform'''
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")


class UI:

    def __init__(self, name):
        self.pages: list[UI._Page] = []
        self.current_page: UI._Page = None
        self.name: str = name
        self.current_page_index: int = 0

    def render(self, page: '_Page'):
        '''print all elements in the provided page'''
        for idx, element in enumerate(page.elements):
            print(f"{idx+1:2}: {element.label}")

    def switch_page_to_index(self, idx: int):
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
                self.switch_page_to_index(self.current_page_index+1)
            if user_input.lower() == 'a':
                self.switch_page_to_index(self.current_page_index-1)

            if user_input.isnumeric() and int(user_input) <= len(self.current_page.elements):
                user_input = int(user_input)
                index = user_input-1
                if self.current_page.elements[index].command:
                    self.current_page.elements[index]()
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

        def add_element(self, name, command=None) -> '_Element':
            element = self._Element(name, command)
            self.elements.append(element)
            return element

        class _Element:
            def __call__(self):
                self.command()

            def __init__(self, label, command):
                self.label = label
                self.command: callable = command
