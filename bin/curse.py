"""showing the evolution in the terminal using curses."""

import sys
if not '.' in sys.path:
    sys.path.insert(0,'.')

import curses
from curses import wrapper

from conway import FiniteGrid

fg = FiniteGrid(120, boundary='periodic')
# fg.symbols = ['  ','XX' ]

def main(stdscr):
    """"""
    stdscr.clear()
    fg.curse(stdscr)
    fg.evolve(generations=1000, curse=stdscr, interval=0.05)

    stdscr.refresh()
    stdscr.getch()

wrapper(main)