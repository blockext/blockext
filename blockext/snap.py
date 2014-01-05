from xml.etree import ElementTree 
from xml.etree.ElementTree import Element, SubElement

from blockext import *



INPUT_SELECTORS = {
    "n": "n",
    "s": "s",
    "b": "b",
    "m": "txt",
    "d": "n",
}

def pretty(stuff):
    import xml.dom.minidom
    xml = xml.dom.minidom.parseString(ElementTree.tostring(stuff))
    return xml.toprettyxml()

@handler("snap_extension.xml", display="Download Snap! blocks")
def generate_s2e():
    root = Element("blocks", {
        "app": "Snap! 4.0, http://snap.berkeley.edu",
        "version": "1",
    })
    for name, block in Blockext.blocks.items():
        if block.is_hidden: continue

        defn = SubElement(root, "block-definition", {
            "type": block.shape,
            "category": "other",
        })
        SubElement(defn, "header")
        SubElement(defn, "code")
        inputs = SubElement(defn, "inputs")

        input_names = inspect.getargspec(block.func).args
        defaults = list(block.defaults)
        selector = ""
        for part in Block.INPUT_RE.split(block.text):
            if part.startswith("%") and part != "%%":
                shape = part[1]
                input_ = SubElement(inputs, "input", {
                    "type": "%{shape}".format(shape=INPUT_SELECTORS[shape]),
                    "readonly": "true" if shape == "m" else "",
                })
                default = (defaults.pop(0) if defaults else "") or ""
                input_.text = unicode(default)
                if shape in "md":
                    options = SubElement(input_, "options")
                    menu_name = part[3:]
                    options.text = "\n".join(Blockext.menus[menu_name])
                    # TODO menus

                input_name = input_names.pop(0) if input_names else ""
                part = "%'{name}'".format(name=input_name)
            selector += part
        defn.attrib["s"] = selector

        http_block = Element("block", s="reportURL")
        join_block = SubElement(http_block, "block", s="reportJoinWords")
        list_ = SubElement(join_block, "list")
        url = "localhost:{port}/{name}".format(port=Blockext.port, name=name)
        SubElement(list_, "l").text = url
        input_names = inspect.getargspec(block.func).args
        for name in input_names:
            SubElement(list_, "l").text = "/"
            encode = SubElement(list_, "block", s="reportTextFunction")
            l = SubElement(encode, "l")
            SubElement(l, "option").text = "encode URI component"
            SubElement(encode, "block", var=name)

        script = SubElement(defn, "script")
        if block.shape == "command":
            selector = "doRun" if block.is_blocking else "fork"
            run = SubElement(script, "block", s=selector)
            ring = SubElement(run, "block", s="reifyReporter")
            lambda_ = SubElement(ring, "autolambda")
            lambda_.append(http_block)
        else: # reporter, predicate
            SubElement(script, "block", s="doReport").append(http_block)

    # It's useful to change this to "application/xml" while debugging.
    return ("application/octet-stream", ElementTree.tostring(root))



