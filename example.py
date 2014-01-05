
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

menu("pizza", ["tomato", "cheese", "hawaii"])

@reporter("colour of %m.pizza flavour pizza")
def pizza_colour(pizza="tomato"):
    return {
        "tomato": "red",
        "cheese": "yellow",
        "hawaii": "orange",
    }[pizza]

@reporter("id %s")
def id(text):
    return text

@problem
def my_problem():
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

