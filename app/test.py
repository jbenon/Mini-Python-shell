import readline

WORDS = ["alpha", "alpine", "alpinist", "beta", "gamma"]


def completer(text, state):
    # recompute matches every call; no global iteration state
    matches = [w for w in WORDS if w.startswith(text)]
    return matches[state] if state < len(matches) else None


readline.set_completer(completer)

readline.parse_and_bind("tab: complete")
readline.parse_and_bind("set show-all-if-unmodified on")

s = input("> ")  # type: al + TAB, TAB
print("You typed:", s)
