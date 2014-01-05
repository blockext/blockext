from __future__ import unicode_literals

from cgi import escape
import inspect
import itertools
import re
import threading
import time
try:
    from urllib import quote
    from urllib import unquote as _unquote_str
    def unquote(part):
        part = str(part)
        return _unquote_str(part).decode("utf-8")
except ImportError:
    from urllib.parse import unquote, quote
try:
    from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
    from SocketServer import ThreadingMixIn
except ImportError:
    from http.server import HTTPServer, BaseHTTPRequestHandler
    from socketserver import ThreadingMixIn

# TODO rewrite entire thing for package manager.
# TODO error handling



# TODO I'm sure this isn't right
try:
    unicode
    unichr
except NameError:
    unicode = str
    unichr = chr


def unquote_unicode(text):
    def unicode_unquoter(match):
        c = unichr(int(match.group(1), 16))
        # urlib.unquote doesn't like Unicode.
        # So, we simply URL-encode the character again -- but this time, the
        # "correct" way!
        return quote(c.encode("utf-8"))
    return re.sub(r'%u([0-9a-fA-F]{4})', unicode_unquoter, text)


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""


class Blockext(BaseHTTPRequestHandler):
    # HTTPServer makes one Blockext instance for each request.

    blocks = {}
    _handlers = {}
    menus = {}
    name = "A blockext extension"
    filename = "extension"
    port = 8080

    requests = {}

    def log_message(self, format, *args):
        if isinstance(args[0], str) and args[0].startswith("GET /poll"):
            return
        return BaseHTTPRequestHandler.log_message(self, format, *args)

    @classmethod
    def handlers(cls):
        handlers = {}
        for name, func in cls._handlers.items():
            name = name.format(**vars(cls))
            handlers[name] = func
        return handlers

    def do_GET(self):
        is_browser = "text/html" in self.headers.get("Accept", "")
        mime_type = "text/plain"

        path = self.path.split("/")[1:]
        path = [unquote(unquote_unicode(p)) for p in path]
        name = path[0]
        args = path[1:]

        func = self.handlers().get(name, self.blocks.get(name, None))
        if func:
            if isinstance(func, Block):
                response = func(*args)
                mime_type = "text/plain"
            elif "is_browser" in inspect.getargspec(func).args:
                (mime_type, response) = func(is_browser=is_browser, *args)
            else:
                (mime_type, response) = func(*args)
            status = 200
        else:
            response = "ERROR: Not found"
            status = 404

        if isinstance(response, bytes):
            response = response.decode("utf-8")
        else:
            response = unicode(response)

        if is_browser and mime_type == "text/plain":
            # Some browsers seem to hate plain text.
            response = u"""<!DOCTYPE html>
            <meta charset="utf8">
            <title>{title}</title>
            <pre>{response}</pre>
            """.format(title=name, response=escape(response))
            mime_type = "text/html"

        response = response.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Length", str(len(response)))
        self.send_header("Content-Type", mime_type)
        if mime_type == "application/octet-stream":
            self.send_header("Content-Disposition", "attachment")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        self.wfile.write(response)

    @classmethod
    def register(cls, name, block):
        cls.blocks[name] = block

    @classmethod
    def register_handler(cls, name, func, hidden=False, display=None):
        cls._handlers[name] = func
        func.is_hidden = hidden
        func.display = display


def handler(name, **kwargs):
    def wrapper(func):
        Blockext.register_handler(name, func, **kwargs)
        return func
    return wrapper


def menu(name, values):
    Blockext.menus[name] = list(map(unicode, values))


@handler("", hidden=True)
def index(is_browser=False):
    if is_browser:
        html = """<!DOCTYPE html>
        <meta charset="utf8">
        <title>blockext</title>

        <style>
        body { font-family: sans-serif; }
        a { color: #20e; text-decoration: none; }
        a:hover { text-decoration: underline; }
        ul { padding-left: 1em; }
        </style>
        """

        html += "<h1>{name}</h1>".format(name=escape(Blockext.name))

        html += "<ul>"
        handlers = Blockext.handlers()
        for name in sorted(handlers):
            func = handlers[name]
            if func.is_hidden: continue
            html += '<li><a href="/{path}">{display}</a>'.format(
                path=escape(name),
                display=escape(func.display or name),
            )
        html += "</ul>"

        html += "<h2>Blocks</h2>"
        html += "<ul>"
        for name in sorted(Blockext.blocks):
            block = Blockext.blocks[name]
            if block.is_hidden: continue
            parts = [name] + block.defaults
            if block.is_blocking: parts.insert(1, "-")
            html += '<li><a href="/{path}">{text}</a>'.format(
                path=escape("/".join(map(unicode, parts))),
                text=escape(unicode(block) +
                            (" *" if block.is_blocking else "")),
            )
        html += "</ul>"
        html += "<small>* = blocking</small>"

        return ("text/html", html)
    else:
        blocks = [n for (n, b) in Blockext.blocks.items() if not b.is_hidden]
        return ("text/plain", "\n".join(blocks))


class Block(object):
    INPUT_RE = re.compile(r'(%.(?:\.[A-z]+)?)')

    SHAPE_FMTS = {
        "predicate": "<%s>",
        "reporter": "(%s)",
    }

    INPUT_DEFAULTS = {
        "n": 0,
        "d": 0,
        "b": False,
    }

    INPUT_FMTS = {
        "n": "(%s)",
        "s": "[%s]",
        "m": "[%s \u25be]",
        "d": "(%s )",
        "b": "<%s>",
    }

    def __init__(self, text, shape, func, blocking=False, hidden=False):
        if blocking and shape != "command":
            raise ValueError("only commands can be blocking")

        self.text = text
        self.shape = shape
        self.func = func
        self.is_blocking = blocking
        self.is_hidden = hidden

        self.arg_shapes = []
        for part in Block.INPUT_RE.split(self.text):
            if part.startswith("%") and part != "%%":
                assert part[1] in "nbsmd"
                if part[1] in "md":
                    assert "." in part
                self.arg_shapes.append(part[1:])

        defaults = list(inspect.getargspec(func).defaults or [])
        padding = len(self.arg_shapes) - len(defaults)
        defaults = [None] * padding  +  defaults
        shape_defaults = map(Block.INPUT_DEFAULTS.get, self.arg_shapes)
        self.defaults = [a or b for (a, b) in zip(defaults, shape_defaults)]

    def __repr__(self):
        return "<Block(%r)>" % self.text

    def __str__(self):
        r = ""
        defaults = list(self.defaults)
        for part in Block.INPUT_RE.split(self.text):
            if part.startswith("%") and part != "%%":
                shape = part[1]
                fmt = Block.INPUT_FMTS.get(shape, "%s")
                value = defaults.pop(0)
                part = fmt % unicode(value or " ")
            r += part
        fmt = Block.SHAPE_FMTS.get(self.shape, "%s")
        return fmt % r

    @staticmethod
    def convert_arg(arg, type_):
        shape = type_[0]
        if shape == "n":
            try:
                arg = int(arg)
            except ValueError:
                try:
                    arg = float(arg)
                except ValueError:
                    arg = 0
        elif shape == "b":
            arg = True if arg == "true" else False if arg == "false" else None
        elif shape == "m":
            menu_name = arg[2:]
            # TODO check in menu options?
        # shape = "d" ?
        return arg

    def __call__(self, *args):
        request_id = None
        if self.is_blocking:
            request_id = args[0]
            args = args[1:]
            Blockext.requests[request_id] = True
        args = [Block.convert_arg(a, t) for (a, t)
                in zip(args, self.arg_shapes)]
        result = self.func(*args)
        if self.shape == "command": result = None
        result = ("true" if result is True else
                  "false" if result is False else
                  "" if result == None else unicode(result))
        if request_id and request_id in Blockext.requests:
            del Blockext.requests[request_id]
        return result



def _shape(shape):
    def decorator(text, **kwargs):
        def wrapper(func):
            selector = func.__name__
            block = Block(text, shape, func, **kwargs)
            Blockext.register(selector, block)
            return block
        return wrapper
    return decorator


command = _shape("command")
reporter = _shape("reporter")
predicate = _shape("predicate")


def run(name="", filename="extension", port=8080):
    blocking_reporters = [b.text for b in Blockext.blocks.values()
                          if b.shape != "command" and
                          not all(shape[0] in "md" for shape in b.arg_shapes)]
    if blocking_reporters:
        print("WARNING: Scratch 2.0 doesn't support blocking reporters yet.")
        print("Affects: " + "\n         ".join(blocking_reporters))
        print("")

    Blockext.name = name
    Blockext.filename = filename
    Blockext.port = port
    server = ThreadedHTTPServer(('localhost', port), Blockext)
    print('Listening on {}'.format(port))
    server.serve_forever()


import blockext.scratch
import blockext.snap
