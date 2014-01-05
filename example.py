
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



"""
@predicate("true or false")
def tf():
    import random
    return random.choice((True, False))

@reporter("numify %b")
def numify(value):
    return int(not value)

@command("set light to %b")
def set_light(boolean_value):
    print("light is {}".format("on" if boolean_value else "off"))

menu("city", ["Boston", "Bournemouth", "Barcelona", "Belgium"])

@reporter("lookup weather in %m.city", blocking=True)
def weather(city="Boston"):
    import time
    return "{weather} in {city}".format(city=city,
        weather=["sunny", "cloudy", "rainy", "snowy"][int(time.time() % 4)])

menu("motor", [1, 2, 3, "A", "B", "C"])

@command("move motor %d.motor by %n degrees", blocking=True)
def move_motor(motor="A", angle=4):
    print "move {motor} by {angle} degrees!".format(motor=motor, angle=angle)
    time.sleep(1)
    print "..."

@reporter("light sensor value")
def light():
    import random
    return random.randint(0, 100)

@command("drive %n steps")
def move(steps):
    print("." * steps)


            [" ", "beep", "playBeep"],
            [" ", "set beep volume to %n", "setVolume", 5],
            ["r", "beep volume", "volume"],
            [" ", "order %m.pizzaFlavour pizza for %m.deliverOrCollect",
    "orderPizza"],
            ["r", "colour of %m.pizzaFlavour pizza", "pizzaColour"],
            ["r", "random upto %n", "randomThingy"]
        ],
        "menus": {
            "pizzaFlavour": ["tomato", "cheese", "mozarella", "hawaiian"],
            "deliverOrCollect": ["delivery", "collection"]
        }
    }
"""

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

