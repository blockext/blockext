from __future__ import unicode_literals

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

@handler("snap_{filename}.xml", display="Download Snap! blocks")
def generate_xml(is_browser=False):
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

        if block.help_text:
            comment = SubElement(defn, "comment", w="360", collapsed="false")
            comment.text = block.help_text

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
        if block.is_blocking:
            url += "/-" # Blank request id
        SubElement(list_, "l").text = url
        input_names = inspect.getargspec(block.func).args
        for name in input_names:
            SubElement(list_, "l").text = "/"
            encode = SubElement(list_, "block", s="reportTextFunction")
            l = SubElement(encode, "l")
            SubElement(l, "option").text = "encode URI component"
            join = SubElement(encode, "block", s="reportJoinWords")
            SubElement(join, "block", var=name)

        if block.shape == "command":
            script_xml = """
            <script>
                <block s="{selector}">
                    <block s="reifyReporter">
                        <autolambda>
                            {http_block_xml}
                        </autolambda>
                    </block>
                </block>
            </script>
            """.format(
                selector="doRun" if block.is_blocking else "fork",
                http_block_xml="{http_block_xml}",
            )
        elif block.shape == "predicate":
            script_xml = """
            <script>
                <block s="doDeclareVariables">
                    <list>
                        <l>result</l>
                    </list>
                </block>
                <block s="doSetVar">
                    <l>result</l>
                    {http_block_xml}
                </block>
                <block s="doIf">
                    <block s="reportEquals">
                        <block var="result"/>
                        <l>true</l>
                    </block>
                    <script>
                        <block s="doSetVar">
                            <l>result</l>
                            <block s="reportTrue"/>
                        </block>
                    </script>
                </block>
                <block s="doIf">
                    <block s="reportEquals">
                        <block var="result"/>
                        <l>false</l>
                    </block>
                    <script>
                        <block s="doSetVar">
                            <l>result</l>
                            <block s="reportFalse"/>
                        </block>
                    </script>
                </block>
                <block s="doReport">
                    <block var="result"/>
                </block>
            </script>
            """
        elif block.shape == "reporter":
            script_xml = """
            <script>
                <block s="doReport">
                    {http_block_xml}
                </block>
            </script>
            """

        script = ElementTree.fromstring(script_xml.format(
            http_block_xml=ElementTree.tostring(http_block),
        ))
        defn.append(script)

    # It's useful to change this to "application/xml" while debugging.
    return ("application/octet-stream", ElementTree.tostring(root))

