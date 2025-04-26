import tuikit


def hello():
    print("test")


def say(*what):
    for s in what:
        print(s)


def add(a, b):
    print(a+b)


def switch_ui_to_page_idx(idx: int):
    ui.set_page_to_index(idx)


ui = tuikit.UI()
page = ui.add_page('testpage')
page2 = ui.add_page('secpage')

for i in range(200):
    page.add_element(f'\r{i}: color', color=tuikit.FLASHING)

# page.add_element('im red!', color=tuikit.SELECTED)
ui.loop()

# print(ui.set_page.__code__.co_varnames)
# page = ui.add_page('Testing')
# page2 = ui.add_page('page2')
# page3 = ui.add_page('page3')

# page.add_element('switch to page 3', ui.set_page, page3)
# page.add_element('hello', hello)

# page2.add_element('say', say, params=(1, 2, 3, 4, 5))
# page2.add_element('smth')

# page3.add_element('page3 smth')
# page3.add_element('to page 1', ui.set_page, page)

# ui.loop(stop=True)
