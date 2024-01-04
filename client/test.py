#
# This file supports http://davesteele.github.io/development/2021/08/29/python-asyncio-curses/
#

import asyncio
import curses
from abc import ABC, abstractmethod
from curses import ERR, KEY_RESIZE, curs_set, wrapper

import _curses


class Display(ABC):
    def __init__(self, stdscr: "_curses._CursesWindow"):
        self.stdscr = stdscr
        self.done: bool = False
        self.buffer: str = ""

    @abstractmethod
    def make_display(self) -> None:
        pass

    @abstractmethod
    def handle_char(self, char: int) -> None:
        pass

    def set_exit(self) -> None:
        self.done = True

    async def run(self) -> None:
        curs_set(0)
        self.stdscr.nodelay(True)

        self.make_display()

        while not self.done:
            char = self.stdscr.getch()
            if char == ERR:
                await asyncio.sleep(0.1)
            elif char == KEY_RESIZE:
                self.make_display()
            else:
                self.handle_char(char)


class MyDisplay(Display):
    def make_display(self) -> None:
        msg1 = "Resize at will"
        msg2 = "Press 'q' to exit"

        maxy, maxx = self.stdscr.getmaxyx()
        self.stdscr.erase()

        self.stdscr.box()
        self.stdscr.refresh()

        self.input_height, self.chat_height = 1, curses.LINES - 2
        self.chat_window = curses.newwin(self.chat_height, curses.COLS, 0, 0)
        self.input_window = curses.newwin(
            self.input_height, curses.COLS, self.chat_height, 0
        )
        self.chat_window.scrollok(True)
        self.input_window.addstr(0, 0, "> ")

    def handle_char(self, char: int) -> None:
        if chr(char) == "q":
            self.set_exit()
        elif char == 10:
            self.buffer = ""
        else:
            self.buffer += chr(char)

        self.stdscr.addstr(0, 2, f"message: {self.buffer}")


async def display_main(stdscr):
    display = MyDisplay(stdscr)
    await display.run()


def main(stdscr) -> None:
    return asyncio.run(display_main(stdscr))


if __name__ == "__main__":
    wrapper(main)
