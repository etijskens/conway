"""Showing the evolution in the terminal using the curses Python module.

Check out https://www.youtube.com/watch?v=Db4oc8qc9RU and its successors
for working with curses.
"""

import sys
if not '.' in sys.path:
    sys.path.insert(0,'.')

import curses
from curses import wrapper

from conway import FiniteGrid

fg = FiniteGrid(30, boundary='periodic')
# fg.symbols = ['  ','XX' ]

def main(stdscr):
    """"""
    stdscr.clear()
    fg.curse(stdscr)
    fg.evolve(n_generations=1000, curse=stdscr, interval=0.05)

    stdscr.refresh()
    stdscr.getch()

wrapper(main)