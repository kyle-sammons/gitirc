import sys
from blessed import Terminal
from pygit2 import clone_repository
from uuid4 import uuid4

from input import Input
from graphics import Graphics

from typing import List

class Main():
    def __init__(self):
        self.term = Terminal()
        self.input = Input(self.term)
        self.graphics = Graphics(self.term)

        self.filler = ['~'] * (self.term.height - 1)
        self.messages = []
        self.repo = None
        self.gitirc_file = None

    def register_server(self, trailing_words: List[str]):
        repo_name = trailing_words[0]
        repo_url = "".join(trailing_words[1:])
        repo_path = f"servers/{repo_name}"

        self.repo = clone_repository(repo_url, repo_path)

        # Just create the file for now
        filename = repo_path + "/.gitirc"
        with open(filename, "w"):
            self.gitirc_file = filename


    def on_quit(self, trailing_words: List[str]):
        # TODO: Post quit message
        sys.exit(0)

    def on_input(self, buffer):
        self.graphics.redraw(self.filler, buffer)

    def start(self):
        with self.term.fullscreen(), self.term.cbreak():
            self.graphics.redraw(self.filler, "")

            self.input.on_command("quit", self.on_quit)
            self.input.on_command("server", self.register_server)
            self.input.on_input(self.on_input)

            self.input.start_input_loop()
    

if __name__ == "__main__":
    main = Main()
    main.start()
