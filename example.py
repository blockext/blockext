"""
blockext spec
for tim
because he's too good for a doc file

Example code:
"""

import blockext

blockext.PORT = 1234

@blockext.predicate("/tf")
def tf():
    blockspec = "true or false"
    return random.choice(True, False)


@blockext.reporter("/weather", blocking=True)
def weather(city):
    blockspec = "current weather in %s"
    return weatherIn(city)

@blockext.reporter("/light")
def light():
    blockspec = "light sensor value"
    return lightsensor.get()

@blockext.stack("/move")
def move(degrees):
    blockspec = "move %n degrees"
    move(degrees)

blockext.generate_extension(blockext.SCRATCH, "extension.json")
blockext.generate_extension(blockext.SNAP, "extension.xml")
if __name__ == "__main__":
    blockext.run()


# I suppose a launcher could do that on demand

# Or run() could do it for you. Really I wanted you to think about *why* you're
# doing stuff.
