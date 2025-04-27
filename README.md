# Tuikit
A terminal UI solution for building user-friendly interactive interfaces with ease.

## Example usage
### Add Elements and Pages
```
ui = tuikit.UI()
page1 = ui.add_page()
page1.add_element('Banana')
page1.add_element('Apple')
page1.add_element('Orange')
page2.add_element('Bread')
page2.add_element('Milk')
ui.loop()
```
This will output:
```
 P: Untitled page
 Untitled UI 1/2

 1: Banana
 2: Apple
 3: Orange
>>> 
 ```
You can switch pages by pressing **A** or **D** on your keyboard.

### Make Elements Do Something
Suppose you have a `hello` function:
```
def hello():
    print("Hi there.")
```
You can bind it to an element.
```
ui = tuikit.UI()
page = ui.add_page()
page.add_element('say hello!', command=hello)
ui.loop(stop=True)
```
Use stop=True to pause after selecting an element, so we can actually see what our element does.

Now, selecting an element will print:
```
Hi there.
```

### Passing Arguments To Commands
You can also pass parameters to commands:
```
def product(*nums):
    prod = 1
    for num in nums:
        prod*=num
    print(prod)

def say(what):
    print(what)

def add(a,b):
    print(a+b)
...
page.add_element('Add numbers', command=add, params=(1,2))
page.add_element('Say Hello', command=say, params="Hello")
page.add_element('Multiply', command=product, params=(1,2,3,4,5))
...
```
### Add Color To Elements
You can style elements using tuikit.Style
```
page.add_element('I am red!', color=tuikit.Style.RED)
```
### Custom Loops
Don't like UI.loop()?

You can manually control the flow using `UI.render()` and `UI.ask_input()`:

```
menu = tuikit.UI()

for _ in range(5):
    page = menu.add_page()
    for _ in range(10):
        page.add_element("Untitled element")

while True:
    menu.render()
    cur_page = menu.current_page
    selected_element = menu.ask_input()
    if selected_element:
        cur_page.elements[selected_element - 1].color = tuikit.Style.INVERTED

    tuikit.cls()
```
This approach lets you add dynamic behavior, such as changing the selected element's style, as shown above.

## UI attributes

- `name: str` - Name of the ui
- `header: str` | None = Header to show when rendering.
If not set, an automatic header is generated, e.g.:

```
P: CURRENT_PAGE_NAME
UI_NAME 4/4
```

- `show_name: bool` - if True, auto-header will show UI name.
- `show_current_page: bool` - if True, auto-header will show current page index.
- `show_current_page_name: bool` - if True, auto-header will show current page's name.

