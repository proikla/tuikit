# Tuikit
**Tuikit** is a user-friendly python library for building interactive terminal menus with ease.

## Features
- Page navigation (A / D keys)
- Selectable elements
- Styled elements with `tuikit.Style`
- Command binding with arguments
- Full control over the event loop

## Installation
**Tuikit** is fully usable, but it is not yet available for installation via `pip`. You can still use it by downloading the source code directly from this repository.


## Quick start
### Create a simple menu
Elements can be chained easily:
``` python
import tuikit
menu = tuikit.UI()
menu.add_element("Hello").add_element("World")
menu.loop()
```
#### Output:
``` 
P: Untitled page
Untitled UI 1/1 
1: Hello 
2: World 
>>>    
```   

### Multiple pages
``` python
from tuikit import UI

menu = UI()
fruits = menu.add_page('Fruits')
fruits.add_element('Banana')
fruits.add_element('Apple')
fruits.add_element('Orange')

groceries = menu.add_page('Groceries')
groceries.add_element('Bread')
groceries.add_element('Milk')

# append an element to the last page
menu.add_element('Cheese')

menu.loop()
```
#### Output:
``` 
P: Fruits      
Untitled UI 1/2
1: Banana 
2: Apple  
3: Orange 
>>>        
```
Press A and D to navigate between pages.

## Adding Actions
You can bind a function to an element:

``` python
def hello():
    print("Hi there.")

menu = UI()
page = menu.add_page()
page.add_element('Say Hello!', command=hello)

menu.loop(stop=True)
```
Set `stop=True` to pause after executing an action.

## Passing Parameters
To pass arguments to your functions use `params`:
``` python
def add(a, b):
    print(a + b)

def shout(message):
    print(message.upper())

page.add_element('Add numbers', command=add, params=(2, 3))
page.add_element('Shout', command=shout, params="hello world")
```

## Adding Colors
Use `tuikit.Style` to style elements:
``` python
page.add_element("Unavailable", color=tuikit.Style.DIMMED)
```
Combine multiple styles:
``` python
warning_style = tuikit.Style.RED | tuikit.Style.BOLD
page.add_element("Warning!", color=warning_style)
page.add_element("Extra warning!", color=warning_style | tuikit.Style.UNDERSCORE_INTERSECT)
```

## Full control Example
If you want to control the loop manually:
``` python
menu = tuikit.UI()

# Create 5 pages, each with 10 elements
for _ in range(5):
    page = menu.add_page()
    for _ in range(10):
        page.add_element("Element")

# Custom loop 
while True:
    menu.render()
    selected = menu.ask_input()

    if selected: # Change element's style on selection
        page = menu.current_page
        page.elements[selected - 1].color = tuikit.Style.INVERTED

    tuikit.cls()
```
