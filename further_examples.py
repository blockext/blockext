import blockext
from blockext import *



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

@reporter("lookup weather in %m.city")
def weather(city="Boston"):
    import time
    return "{weather} in {city}".format(city=city,
        weather=["sunny", "cloudy", "rainy", "snowy"][int(time.time() % 4)])

menu("motor", [1, 2, 3, "A", "B", "C"])

@command("move motor %d.motor by %n degrees", blocking=True)
def move_motor(motor="A", angle=4):
    print("move {motor} by {angle} degrees!".format(motor=motor, angle=angle))
    time.sleep(1)
    print("...")

@reporter("light sensor value")
def light():
    import random
    return random.randint(0, 100)

@command("drive %n steps")
def move(steps):
    print("." * steps)



if __name__ == "__main__":
    blockext.run("Disappointing UFO", "ufo", 5678)
