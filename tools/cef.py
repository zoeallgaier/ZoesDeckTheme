#!/usr/bin/env python3
"""Inspect the live Steam UI through the CEF remote debugger (stdlib only).

Run ON THE DECK (the debugger listens on 127.0.0.1:8080). Gaming Mode tabs
(SP, QuickAccess_*, MainMenu_*) only exist while Gaming Mode is running.

  tools/cef.py tabs                          list debuggable tabs
  tools/cef.py tree SP [selector] [depth]    DOM outline with readable class names
  tools/cef.py find SP <readable-class>      elements matching e.g. gamepadui_BasicHome
  tools/cef.py eval SP '<js expression>'     run JS, print the JSON result
  tools/cef.py shot SP out.png               screenshot a tab

Tab arguments are regexes matched against the tab title ("SP", "QuickAccess",
"MainMenu", "Steam"...). Steam ships scrambled class names; `tree`/`find`
translate them to the readable names CSS Loader understands, using
~/homebrew/themes/css_translations.json.
"""
import base64
import json
import os
import re
import socket
import struct
import sys
import urllib.request

PORT = int(os.environ.get("CEF_PORT", "8080"))
TRANSLATIONS = os.path.expanduser("~/homebrew/themes/css_translations.json")
READABLE = re.compile(r"^[a-z][a-z0-9]*_[A-Za-z0-9-]+_[A-Za-z0-9]{5}$")
# Same aliases CSS Loader uses: newer Steam titles the main Gaming Mode window
# "Steam Big Picture Mode" rather than "SP".
ALIASES = {"SP": r"^(SP|Steam Big Picture Mode)$"}


def list_tabs():
    with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json", timeout=5) as r:
        return json.load(r)


def pick_tab(pattern):
    tabs = [t for t in list_tabs() if t.get("webSocketDebuggerUrl")]
    exact = [t for t in tabs if t["title"] == pattern]
    pattern = ALIASES.get(pattern, pattern)
    matches = exact or [t for t in tabs if re.search(pattern, t["title"])]
    if not matches:
        sys.exit(f"No tab matches {pattern!r}. Is Gaming Mode running? Try: cef.py tabs")
    return matches[0]


class DevTools:
    """Minimal websocket client, enough for the DevTools protocol."""

    def __init__(self, ws_url):
        hostport, path = ws_url.split("://", 1)[1].split("/", 1)
        host, port = hostport.split(":")
        self.sock = socket.create_connection((host, int(port)), timeout=30)
        key = base64.b64encode(os.urandom(16)).decode()
        self.sock.sendall(
            f"GET /{path} HTTP/1.1\r\nHost: {hostport}\r\nUpgrade: websocket\r\n"
            f"Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\n"
            "Sec-WebSocket-Version: 13\r\n\r\n".encode()
        )
        head = b""
        while b"\r\n\r\n" not in head:
            head += self._read(1)
        if b" 101 " not in head.split(b"\r\n", 1)[0]:
            raise RuntimeError(head.decode(errors="replace"))
        self.next_id = 0

    def _read(self, n):
        buf = b""
        while len(buf) < n:
            chunk = self.sock.recv(n - len(buf))
            if not chunk:
                raise EOFError("websocket closed")
            buf += chunk
        return buf

    def _send(self, text):
        data = text.encode()
        header = bytearray([0x81])
        if len(data) < 126:
            header.append(0x80 | len(data))
        elif len(data) < 65536:
            header.append(0x80 | 126)
            header += struct.pack(">H", len(data))
        else:
            header.append(0x80 | 127)
            header += struct.pack(">Q", len(data))
        mask = os.urandom(4)
        masked = bytes(b ^ mask[i % 4] for i, b in enumerate(data))
        self.sock.sendall(bytes(header) + mask + masked)

    def _recv(self):
        message = b""
        while True:
            b1, b2 = self._read(2)
            length = b2 & 0x7F
            if length == 126:
                length = struct.unpack(">H", self._read(2))[0]
            elif length == 127:
                length = struct.unpack(">Q", self._read(8))[0]
            payload = self._read(length)
            opcode = b1 & 0x0F
            if opcode == 8:
                raise EOFError("websocket closed")
            if opcode in (9, 10):
                continue
            message += payload
            if b1 & 0x80:
                return json.loads(message)

    def call(self, method, **params):
        self.next_id += 1
        self._send(json.dumps({"id": self.next_id, "method": method, "params": params}))
        while True:
            msg = self._recv()
            if msg.get("id") == self.next_id:
                if "error" in msg:
                    raise RuntimeError(msg["error"])
                return msg["result"]

    def evaluate(self, expression):
        res = self.call("Runtime.evaluate", expression=expression,
                        returnByValue=True, awaitPromise=True)
        if "exceptionDetails" in res:
            raise RuntimeError(res["exceptionDetails"].get("exception", {}).get("description"))
        return res["result"].get("value")


def load_translations():
    """Map scrambled class -> readable name, and readable -> scrambled."""
    to_readable, to_live = {}, {}
    try:
        with open(TRANSLATIONS, encoding="utf-8") as fp:
            data = json.load(fp)
    except OSError:
        return to_readable, to_live
    for names in data.values():
        live = names[-1]
        readable = next((n for n in names if READABLE.match(n)), None)
        if readable:
            to_readable[live] = readable
            for n in names[:-1]:
                to_live[n] = live
    return to_readable, to_live


TREE_JS = r"""
(() => {
  const root = document.querySelector(%s);
  if (!root) return null;
  const walk = (el, d) => ({
    tag: el.tagName.toLowerCase(),
    cls: [...el.classList],
    text: el.children.length ? '' : (el.textContent || '').trim().slice(0, 40),
    kids: d > 0 ? [...el.children].map(c => walk(c, d - 1)) : (el.children.length ? '…' : [])
  });
  return walk(root, %d);
})()
"""


def print_tree(node, to_readable, indent=0):
    if node is None:
        print("(selector matched nothing)")
        return
    cls = " ".join("." + to_readable.get(c, c) for c in node["cls"])
    text = f'  "{node["text"]}"' if node["text"] else ""
    print("  " * indent + node["tag"] + (" " + cls if cls else "") + text)
    if node["kids"] == "…":
        print("  " * (indent + 1) + "…")
        return
    for kid in node["kids"]:
        print_tree(kid, to_readable, indent + 1)


def main(argv):
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        print(__doc__)
        return
    cmd = argv[1]
    if cmd == "tabs":
        for t in list_tabs():
            print(f'{t["title"]:<32} {t["url"][:80]}')
        return

    tab = pick_tab(argv[2])
    dt = DevTools(tab["webSocketDebuggerUrl"])
    to_readable, to_live = load_translations()

    if cmd == "tree":
        selector = argv[3] if len(argv) > 3 else "body"
        depth = int(argv[4]) if len(argv) > 4 else 6
        # Accept readable class names in the selector.
        selector = re.sub(r"\.([_a-zA-Z][\w-]*)",
                          lambda m: "." + to_live.get(m.group(1), m.group(1)), selector)
        print_tree(dt.evaluate(TREE_JS % (json.dumps(selector), depth)), to_readable)
    elif cmd == "find":
        name = argv[3]
        live = to_live.get(name, name)
        count = dt.evaluate(f"document.getElementsByClassName({json.dumps(live)}).length")
        print(f"{name} -> .{live}: {count} element(s) in {tab['title']}")
    elif cmd == "eval":
        print(json.dumps(dt.evaluate(argv[3]), indent=2))
    elif cmd == "shot":
        out = argv[3] if len(argv) > 3 else "shot.png"
        # Hidden windows produce no frames, so the capture would hang.
        if dt.evaluate("document.visibilityState") != "visible":
            sys.exit(f"{tab['title']} is not visible on screen, so it has no frame to capture.")
        try:
            data = dt.call("Page.captureScreenshot", format="png")["data"]
        except TimeoutError:
            sys.exit("Screenshot timed out: the window is not rendering frames.")
        with open(out, "wb") as fp:
            fp.write(base64.b64decode(data))
        print(f"saved {out}")
    else:
        sys.exit(f"unknown command {cmd!r}")


if __name__ == "__main__":
    main(sys.argv)
