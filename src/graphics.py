from typing import List

class Graphics():
    def __init__(self, term):
        self.term = term

    def redraw(self, messages: List[str], buffer: str):
        with self.term.location(0, self.term.height - 1):
            for message in messages:
                print(message)
            print(buffer)
