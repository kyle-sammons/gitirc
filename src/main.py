import sys
from blessed import Terminal

from input import Input
from graphics import Graphics

def main():
    term = Terminal()
    inp = Input(term)
    graphics = Graphics(term)

    filler = ['~'] * (term.height - 1)

    with term.fullscreen(), term.cbreak():
        graphics.redraw(filler, "")
        inp.on_command("quit", lambda x: sys.exit(0))
        inp.on_input(lambda buffer: graphics.redraw(filler, buffer))
        inp.start()
    
if __name__ == "__main__":
    main()
