# coding=utf-8
from __future__ import unicode_literals

import time

from blockext import *



class Example:
    def __init__(self):
        self.foo = 0

    def _problem(self):
        if time.time() % 8 > 4:
            return "The Scratch Sensor board is not connected. Foo."

    def _on_reset(self):
        print("""
        Reset! The red stop button has been clicked,
        And now everything is how it was.
        ...
        (Poetry's not my strong point, you understand.)
        """)

    @predicate("not %b")
    def not_(self, value):
        return not value

    @command("say %s for %n secs", is_blocking=True)
    def say_for_secs(self, text="Hello", duration=5):
        print(text)
        time.sleep(duration)

    @command("play note %n")
    def play_note(self, note):
        print("DING {note}".format(note=note))
        time.sleep(2)

    @reporter("colour of %m.pizza flavour pizza", defaults=["tomato"])
    def pizza_colour(self, pizza):
        return {
            "tomato": "red",
            "cheese": "yellow",
            "hawaii": "orange and blue",
        }[pizza]

    @reporter("id %s")
    def id(self, text):
        """Tests strings can get passed from Snap! to Python and back."""
        print(text)
        return text

    @command("set number to %n% units")
    def percent(self, number=42):
        print(number)

    @command("set foo to %s")
    def set_foo(self, value=''):
        self.foo = value

    @reporter("foo")
    def get_foo(self):
        return self.foo

    @command("ü")
    def x(self):
        pass

    @command("set color to %c")
    def set_color(self, c):
        print(c)
    

descriptor = Descriptor(
    name = "Fancy Spaceship",
    port = 1234,
    blocks = get_decorated_blocks_from_class(Example),
    menus = dict(
        pizza = ["tomato", "cheese", "hawaii"],
    ),
)

extension = Extension(Example, descriptor)

if __name__ == "__main__":
    extension.run_forever(debug=True)

