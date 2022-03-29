# -*- coding: utf-8 -*-

"""
Package conway_mac
=======================================

Top-level package for conway_mac.

Conway's game of life
*********************

Some useful/interesting links

* `Game of life <https://nl.wikipedia.org/wiki/Game_of_Life>`_


Concepts
--------
* infinite grid of square cells
* cells are either dead or alive
* each cell has 8 neighbours. Let ``A_ij`` be the number of alive neighbours of cell ``ij``.
  A populated cells remains populated, only if 2 or 3 or its neighbours are populated.
  Otherwise, the cell's population dies (either of loneliness or overpopulation).
  A non-populated cell is populated, if it has exactly 3 populated neighbouring cells
  Note that one must count the neighbours of **all** cells before updating states.

Implementation ideas
--------------------
* We cannot store an infinite grid, as memory is finite.
* We could store only the living cells and their location. That would allow for a finite
  number of cells on an infinite grid. That would be a rather complex idea to begin with
* We could start with a finite grid and use a reflecting boundary, surrounding the grid
  with an extra layer which has the same state as the neighbouring layer on the inside.
  e.g. on a 4x4 grid::

    0 | 0 0 1 0 | 0
    --+---------+--
    0 | 0 0 1 0 | 0
    0 | 0 1 0 0 | 0
    0 | 0 0 1 0 | 0
    0 | 0 1 0 1 | 1
    --+---------+--
    0 | 0 1 0 1 | 1

  I.e., we would store a 6x6 grid with a different rule to update the outer cells.

* We could apply periodic boundary conditions, i.e. the surrounding layer would be a copy
  of the layer at the other end::

    1 | 0 1 0 1 | 0
    --+---------+--
    0 | 0 0 1 0 | 0
    0 | 0 1 0 0 | 0
    0 | 0 0 1 0 | 0
    1 | 0 1 0 1 | 0
    --+---------+--
    0 | 0 0 1 0 | 0

  That would be some sort of infinity.


Let's start off with a finite grid.

"""

__version__ = "0.0.0"

import numpy as np


class FiniteGrid:
    """Naive NxN grid with.

    In order to not have to implement special boundary rules, we make the grid
    (N+2)x(N+2) where the outer layers are ghost cells which are just there to
    make sure that index i-1, i+1, j-1 and j+1 exist for all cells (i,j)::

        0 | 0 0 0 0 | 0
        --+---------+--
        0 | 0 0 1 0 | 0
        0 | 0 1 0 0 | 0
        0 | 0 0 1 0 | 0
        0 | 0 1 0 1 | 0
        --+---------+--
        0 | 0 0 0 0 | 0

    The state of the ghost cells is determined by the boundary conditions:
    * all zeros,
    * reflective boundary condition: the ghost cell has the same state as the cell
      on the inside of the boundary
    * Periodic boundary condition: a ghost cell is a copy of the state at the other
      end, as if the finite grid is repeated in the x and y direction.

    This is a very simple naive approach, with important shortcomings:

    * its finite grid is finite.

    and gross inefficiencies

    * it uses a Python int per cell (=64 bit) to store the state and an extra
      Python int per cell to count the number of neighbouring cells.
      As the count is at most 8, which can be stored with 3 bits, this approach
      actually only uses 4 of 128 allocated bits per cell. That is, almost 97% of
      the allocated memory actually wasted
    * the evolve() method uses two double loops over all cells, which is very
      inefficient

    Think of approaches to cure these problems

    """
    boundary_conditions = ('zero', 'reflect', 'periodic')

    def __init__(self, N=10, boundary='zero'):
        self.N = N
        self.n = N + 2
        rng = np.random.default_rng()
        self.states = rng.integers(0, high=2, size=(N+2,N+2))
        # correct the boundaries
        if 'zero'.startswith(boundary):
            self.bc = 'zero'
            # boundaries are zeros
            self.apply_0bc()

        elif 'reflect'.startswith(boundary):
            self.bc = 'reflect'
            self.apply_rbv()

        elif 'periodic'.startswith(boundary):
            self.bc = 'periodic'
            self.apply_pbc()

        else:
            raise ValueError("boundary not in ('zero', 'reflect', 'periodic')")

        self.counts = np.zeros_like(self.states, dtype=int)
        self.generation = 0

    def apply_bc(self, bc=None):
        if not bc is None:
            self.bc = bc
        if self.bc == 'zero':
            self.apply_0bc()
        elif self.bc == 'reflect':
            self.apply_rbc()
        elif self.bc == 'periodic':
            self.apply_pbc()
        else:
            raise ValueError("boundary not in ('zero', 'reflect', 'periodic')")

    def apply_0bc(self):
        N = self.N
        self.states[:    , 0    ] = 0
        self.states[:    , N + 1] = 0
        self.states[0    , 1:N+1] = 0
        self.states[N + 1, 1:N+1] = 0

    def apply_rbc(self):
        """Apply reflecting boundary condition."""
        N = self.N
        self.states[:, 0    ] = self.states[:, 1]
        self.states[:, N + 1] = self.states[:, N]
        self.states[0, :    ] = self.states[1, :]
        self.states[N + 1, :] = self.states[N, :]

    def apply_pbc(self):
        """Apply periodic boundary condition."""
        N = self.N
        # edges
        self.states[1:N + 1, 0] = self.states[1:N + 1, N]
        self.states[1:N + 1, N + 1] = self.states[1:N + 1, 1]
        self.states[0, 1:N + 1] = self.states[N, 1:N + 1]
        self.states[N + 1, 1:N + 1] = self.states[1, 1:N + 1]
        # corners
        self.states[0    , 0    ] = self.states[N, N]
        self.states[N + 1, N + 1] = self.states[1, 1]
        self.states[0    , N + 1] = self.states[N, 1]
        self.states[N + 1, 0    ] = self.states[1, N]

    def evolve(self, generations=1, draw=True, stop_if_static=False):
        """Let the system evolve over ``generations`` generations."""
        N = self.N
        while generations>0:
            if stop_if_static:
                previous_states = np.copy(self.states)
            for i in range(1,N+1):
                for j in range(1,N+1):
                    self.counts[i, j] = self.states[i-1, j-1] \
                                      + self.states[i-1, j  ] \
                                      + self.states[i-1, j+1] \
                                      + self.states[i  , j-1] \
                                      + self.states[i  , j+1] \
                                      + self.states[i+1, j-1] \
                                      + self.states[i+1, j  ] \
                                      + self.states[i+1, j+1]
            for i in range(1,N+1):
                for j in range(1,N+1):
                    if self.states[i,j] == True: # populated
                        if not self.counts[i,j] in (2,3): # cell population dies
                            self.states[i,j] = False
                    else:
                        if self.counts[i,j] == 3:
                            self.states[i,j] = True

            self.apply_bc()
            self.generation += 1
            generations -= 1
            # stop if all cells are dead
            if np.sum(self.states) == 0:
                generations = 0
            # stop if fixed state
            if stop_if_static:
                if np.all(previous_states == self.states):
                    generations = 0
            if draw:
                self.pdraw(boundary=False)


    def print(self, boundary=True):
        if boundary:
            print(f'BC = {self.bc}')
            for i in range(self.n):
                s = ''
                for j in range(self.n):
                    s += f"{self.states[i, j]} "
                print(s)
        else:
            for i in range(1,self.n-1):
                s = ''
                for j in range(1,self.n-1):
                    s += f"{self.states[i, j]} "
                print(s)
        print()
        

    def pdraw(self, boundary=True):
        """use the terminal to print the grid
        """
        N = self.N
        ri = range(0,N+2) if boundary else range(1,N+1)
        rj = range(0,N+2) if boundary else range(1,N+1)
        for i in ri:
            line = ''
            for j in rj:
                line += u'\u2588\u2588 ' if self.states[i,j] else u'   '
            print(line)
        print(f"generation = {self.generation}")
