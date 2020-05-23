import sys
from blessed import Terminal
from pygit2 import clone_repository, GIT_SORT_REVERSE
from uuid import uuid4

from input import Input
from graphics import Graphics

from typing import List

class Main():
    def __init__(self):
        self.term = Terminal()
        self.input = Input(self.term)
        self.graphics = Graphics(self.term)

        self.filler = ['~'] * (self.term.height - 1)
        self.messages = self.filler
        self.repo = None
        self.gitirc_file = None

    def load_messages(self):
        if self.repo:
            loaded_messages = []
            for commit in self.repo.walk(self.repo.head.target, GIT_SORT_REVERSE):
                message = commit.message.strip()
                loaded_messages.append(f"{commit.committer.raw_name.decode()}: {message}")

            self.messages = (['~'] * ((self.term.height - 1) - len(loaded_messages))) + loaded_messages

    def register_server(self, trailing_words: List[str]):
        repo_name = trailing_words[0]
        repo_url = "".join(trailing_words[1:])
        repo_path = f"servers/{repo_name}"

        self.repo = clone_repository(repo_url, repo_path)

        # Just create the file for now
        filename = repo_path + "/.gitirc"
        with open(filename, "w"):
            self.gitirc_file = filename

        self.load_messages()
        self.graphics.redraw(self.messages, "")


    def on_quit(self, trailing_words: List[str]):
        # TODO: Post quit message
        sys.exit(0)

    def on_input(self, buffer):
        self.graphics.redraw(self.messages, buffer)

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
