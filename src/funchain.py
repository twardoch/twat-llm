#!/usr/bin/env python3


def tolower(s):
    return s.lower()


from mallmo import ask_chain

output = ask_chain(
    data="My name is Adam Twardoch",
    steps=[
        "Convert the full name to all caps in: $input",
        "Translate into Polish:",
        tolower,
    ],
)
