from blessed import Terminal


def redraw(term, messages, buffer):
    with term.location(0, term.height - 1):
        for message in messages:
            print(message)
        print(buffer)


def input_loop(term: Terminal):
    message = ""
    buffer = ""
    filler = ['~'] * (term.height - 1)

    messages = filler

    while message != "/quit":
        key = term.inkey()
        if key.name == "KEY_BACKSPACE" or key.name == "KEY_DELETE":
            buffer = buffer[:-1]
        elif key.name == "KEY_ENTER":
            message = buffer
            buffer = ""
        else:
            buffer += key

        redraw(term, messages, buffer)


def main():
    term = Terminal()

    with term.fullscreen(), term.cbreak():
        filler = ['~'] * (term.height - 1)

        messages = filler
        redraw(term, messages, '')
        input_loop(term)
    
if __name__ == "__main__":
    main()
