*********************
Conway's game of life
*********************

The Game of Life, also known simply as *Life*, is a cellular automaton devised by the British
mathematician John Horton Conway in 1970. The concepts are well explained here:
`Game of life <https://nl.wikipedia.org/wiki/Game_of_Life>`_.

Documentation is to be found at

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

*

Documentation:
--------------
https://conway.readthedocs.io
