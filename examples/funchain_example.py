#!/usr/bin/env python3


from mallmo import ask_chain


def tolower(s):
    return s.lower()


output = ask_chain(
    data="My name is Adam Twardoch",
    steps=[
        "Convert the full name to all caps in: $input",
        "Translate into Polish:",
        tolower,
    ],
)
