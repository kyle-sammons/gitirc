import time
from blessed import Terminal
from typing import Dict, List, Callable

class Input():
    def __init__(self, term: Terminal):
        self.term = term
        self.command_handlers: Dict[str, Callable[[List[str]], None]] = {}
        self.input_handlers: List[Callable[[str], None]] = []
        self.enter_handlers: List[Callable[[str], None]] = []

    def on_command(self, command: str, func: Callable[[str], None]):
        self.command_handlers[command] = func

    def on_input(self, func: Callable[[str], None]):
        self.input_handlers.append(func)

    def on_enter(self, func: Callable[[str], None]):
        self.enter_handlers.append(func)

    def handle_command(self, command: str, trailing_words: List[str]):
        if command in self.command_handlers:
            self.command_handlers[command](trailing_words)

    def handle_input(self, buffer: str):
        for handler in self.input_handlers:
            handler(buffer)

    def handle_enter(self, buffer: str):
        for handler in self.enter_handlers:
            handler(buffer)

    def start_input_loop(self, temp_callback_test):
        buffer = ""
        start = time.time()
        while True:
            if (time.time() - start) >= 3:
                temp_callback_test()
                start = time.time()

            key = self.term.inkey()
            if key.name == "KEY_BACKSPACE" or key.name == "KEY_DELETE":
                buffer = buffer[:-1]
            elif key.name == "KEY_ENTER":
                # A slash demarcates a command
                if len(buffer) > 0 and buffer[0] == "/":
                    words = buffer.split()
                    self.handle_command(words[0][1:], words[1:])
                else:
                    self.handle_enter(buffer)
                buffer = ""
            else:
                buffer += key
            self.handle_input(buffer)
