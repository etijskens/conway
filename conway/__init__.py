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
    (N+2)x(N+2) where the outer layers are always zero::

        0 | 0 0 0 0 | 0
        --+---------+--
        0 | 0 0 1 0 | 0
        0 | 0 1 0 0 | 0
        0 | 0 0 1 0 | 0
        0 | 0 1 0 1 | 0
        --+---------+--
        0 | 0 0 0 0 | 0

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

    def print(self):
        if self.bc == 'zero':
            for i in range(1,self.n-1):
                s = ''
                for j in range(1,self.n-1):
                    s += f"{self.states[i, j]} "
                print(s)
        else:
            print(f'BC = {self.bc}')
            for i in range(self.n):
                s = ''
                for j in range(self.n):
                    s += f"{self.states[i, j]} "
                print(s)
        print()

    def evolve(self):
        """loop over all cells and count its alive neighbours."""
        N = self.N

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
