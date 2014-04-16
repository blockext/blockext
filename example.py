# coding=utf-8

import blockext
from blockext import *



@predicate("not %b")
def not_(value):
    return not value

@command("say %s for %n secs", blocking=True)
def say_for_secs(text="Hello", duration=5):
    import time
    print(text)
    time.sleep(duration)


@command("play note %n")
def play_note(note):
    print("DING {note}".format(note=note))
    time.sleep(2)

menu("pizza", ["tomato", "cheese", "hawaii", "nothing",
               "spinach and cauliflower", "empty return value",
               "cheese and tomato", "fancy",
               "ü",
               "/",
               ])

@reporter("colour of %m.pizza flavour pizza")
def pizza_colour(pizza="tomato"):
    return {
        "tomato": "red",
        "cheese": "yellow",
        "cheese and tomato": "YELLOW",
        "hawaii": "orange AND BLUE",
        "spinach and cauliflower": "GREEN ü",
        "empty return value": "",
        "nothing": "",
        "/": "SLASH",
        u"ü": "unicode",
        u"fancy": "❤☀☆☂",
    }[pizza]

@reporter("spaaace")
def getSpaaace():
    return "space space space space space!"

@reporter("id %s")
def id(text):
    """Tests strings can get passed from Snap! to Python and back."""
    print(text)
    return text

@command("set number to %n% units")
def percent(number=42):
    print(number)

foo = None

@command("set foo to %s")
def set_foo(value=''):
    global foo
    foo = value

@reporter("foo")
def get_foo():
    return foo

@command("ü")
def x(): pass

@problem
def my_problem():
    if time.time() % 8 > 4:
        return "The Scratch Sensor board is not connected. Foo."

@reset
def my_reset():
    print("""
    Reset! The red stop button has been clicked,
    And now everything is how it was.
    ...
    (Poetry's not my strong point, you understand.)
    """)



if __name__ == "__main__":
    blockext.run("Fancy Spaceship", "spaceship", 1234)

