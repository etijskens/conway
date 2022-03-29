.. include:: hyperlinks.rst

*********************
Conway's game of life
*********************

The Game of Life, also known simply as *Life*, is a cellular automaton devised by the British
mathematician John Horton Conway in 1970. The concepts are well explained here:
`Game of life <https://nl.wikipedia.org/wiki/Game_of_Life>`_.

Documentation is to be found at https://conway.readthedocs.io.

Concepts
--------
* infinite grid of square cells.
* cells are either dead or alive,
* each cell evolves according to the following rules:

  * A populated cells remains populated, only if 2 or 3 or its neighbours are populated.
    Otherwise, the cell's population dies (either of loneliness or overpopulation).
  * A non-populated cell is populated, if it has exactly 3 populated neighbouring cells
  * Note that one must count the living neighbours of **all** cells before updating states.

Implementation ideas
--------------------
* We cannot store an infinite grid, as memory is finite.
* We could store only the living cells and their location. That would allow for a finite
  number of cells on an infinite grid. This is  a rather complex idea to begin with.
* We could start with a finite grid and experiment with different kind of boundary conditions,
  surrounding the grid with an extra layer, such that all inner cells have 8 neighbours.
* Periodic boundary conditions would be some sort of infinity.

Example scripts
---------------

The ``bin/`` directory contains a few example scripts that can be modified at liberty. All use
the ``conway.FiniteGrid`` class which is documented in the API section.

* ``evolve.py``: generates a randomly populated finite grid and evolves it, printing the generations
  to the terminal. Run in the ``conway`` project directory as::

    > python bin/evolve.py
    ...

* ``animate.py``: as ``evolve.py``, but uses the Python matplotlib_ module to animate the evolution.
  to the terminal. Run in the ``conway`` project directory as::

    > python bin/animate.py
    ...

  As an animation, this isn't terrible..., but it allows you to inspect the generations one by one,
  scrolling through the terminal.

* ``curses.py``: as ``evolve.py``, but uses the Python curses_ module to animate the evolution.
  to the terminal. Run in the ``conway`` project directory as::

    > python bin/curse.py
    ...

  .. note::

    The windows version of Python does not include curses. Use UniCurses_ instead.

************
Project work
************

The ``conway.FiniteGrid`` class is a very simple naive approach to Conway's
Game of Life, with important shortcomings:

* Its finite grid is finite.

It also has gross inefficiencies:

* It uses a Python ``int`` per cell (=64 bit) to store the state and an extra
  Python ``int`` per cell to count the number of neighbouring cells.
  As the count is at most 8, which can be stored with 3 bits, this approach
  actually only uses 4 of 128 allocated bits per cell. That is, almost 97% of
  the allocated memory actually wasted!
* the evolve() method uses two double loops over all cells, which is very
  inefficient.

Assignment
----------

Think of approaches to cure these problems and implement them. Use ``conway.FiniteGrid``
as a baseline and time it to judge your progress.

Here are some suggestions:

* better data structures
* numba_ acceleration
* low-level implementations
* Vectorization
* multicore parallellization
* multinode parallellization

Good luck!


