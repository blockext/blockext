import json

from blockext import *



CROSSDOMAIN_XML = """
<?xml version="1.0"?>
<cross-domain-policy>
    <allow-access-from domain="*" to-ports="*"/>
</cross-domain-policy>
"""

@handler("crossdomain.xml", hidden=True)
def crossdomain(is_browser=False):
    return ("application/xml", CROSSDOMAIN_XML)

BLOCK_SHAPES = {
    "command": " ",
    "reporter": "r",
    "predicate": "b",
}

@handler("scratch_extension.s2e", display="Download Scratch 2.0 extension")
def generate_s2e():
    extension = {
        "extensionName": Blockext.name,
        "extensionPort": Blockext.port,
        "blockSpecs": [],
        "menus": Blockext.menus,
    }
    for name, block in Blockext.blocks.items():
        if block.is_hidden: continue
        shape = BLOCK_SHAPES[block.shape]
        if block.shape == "command" and block.is_blocking:
            shape = "w"
        blockspec = [shape, block.text, name] + block.defaults
        extension["blockSpecs"].append(blockspec)
    return ("application/octet-stream", json.dumps(extension))


def menu_permutations(arg_shapes):
    if not arg_shapes:
        yield []
        return
    input_selector = arg_shapes[0]
    menu_name = input_selector[2:]
    options = Blockext.menus[menu_name]
    for rest in menu_permutations(arg_shapes[1:]):
        for value in options:
            yield [value] + rest


@handler("poll", hidden=True)
def poll(is_browser=False):
    lines = ""
    for name, block in Blockext.blocks.items():
        if block.is_blocking: continue
        if block.shape not in ("reporter", "predicate"):
            continue
        if all(shape[0] in "md" for shape in block.arg_shapes):
            for args in menu_permutations(block.arg_shapes):
                lines += "{path} {result}\n".format(
                    path="/".join([name] + args),
                    result=block(*args)
                )
    return ("text/plain", lines)

@reporter("", hidden=True)
def _problem():
    return "The Scratch Sensor board is not connected.\xe2\x80\xa8 Foo."

