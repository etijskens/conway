# -*- coding: utf-8 -*-

"""
Package conway
==============

Top-level package for conway

"""

__version__ = "0.4.2"

import numpy as np
import pickle
import time


class FiniteGrid:
    """Naive NxN grid with different boundary conditions. Cells are randomly assigned
    state (dead or alive).

    :param int N: number of cells in the X and Y direction.
    :param str boundary: boundary condition: ``zero``, ``reflecting``, or ``periodic``.
    :param bool dump: pickle the generated FiniteGrid object. (Practical if you
        discover a nice pattern and you want to view it again.
    :param bool load: if True, load a file with a pickled FiniteGrid object, e.g. to
        view its evolution again.
    :param str filename: name of the file to be dumped or loaded.

    In order to not have to implement special boundary rules, we make the grid
    (N+2)x(N+2) where the outer layers are ghost cells which are just there to
    make sure that index i-1, i+1, j-1 and j+1 exist for all cells (i,j)::

        . | . . . .  | .
        --+---------+--
        . | 0 0 1 0 | .
        . | 0 1 0 0 | .
        . | 0 0 1 0 | .
        . | 0 1 0 1 | .
        --+---------+--
        . | . . . . | .

    The state of the ghost cells is determined by the boundary conditions:

    * all zeros::

        0 | 0 0 0 0 | 0
        --+---------+--
        0 | 0 0 1 0 | 0
        0 | 0 1 0 0 | 0
        0 | 0 0 1 0 | 0
        0 | 0 1 0 1 | 0
        --+---------+--
        0 | 0 0 0 0 | 0

    * reflective boundary condition: the ghost cell has the same state as the cell
      on the inside of the boundary::

        0 | 0 0 1 0 | 0
        --+---------+--
        0 | 0 0 1 0 | 0
        0 | 0 1 0 0 | 0
        0 | 0 0 1 0 | 0
        0 | 0 1 0 1 | 1
        --+---------+--
        0 | 0 1 0 1 | 1

    * Periodic boundary condition: a ghost cell is a copy of the state at the other
      end, as if the finite grid is repeated in the x and y direction::

        1 | 0 1 0 1 | 0
        --+---------+--
        0 | 0 0 1 0 | 0
        0 | 0 1 0 0 | 0
        0 | 0 0 1 0 | 0
        1 | 0 1 0 1 | 0
        --+---------+--
        0 | 0 0 1 0 | 0

    """
    boundary_conditions = ('zero', 'reflect', 'periodic')

    def __init__(self, N=10, boundary='zero', dump=False, load=False, filename='conway'):
        if load:
            fg = FiniteGrid.load(filename=filename)
            # transfer all properties from fg to self
            self.__dict__ = fg.__dict__

        else:
            self.N = N
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

            self.generation = 0
            self.counts = None
            self.symbols = ' X'

            if dump:
                self.dump(filename=filename)


    def apply_bc(self, bc=None):
        """Apply a boundary condition to this FiniteGrid object.

        :param str bc: a string identifying the type of boundary condition we want to apply.
        """
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
        """Apply the zero boundary condition, i.e. surround this FiniteGrid
        object by zeros.
        """
        N = self.N
        self.states[:    , 0    ] = 0
        self.states[:    , N + 1] = 0
        self.states[0    , 1:N+1] = 0
        self.states[N + 1, 1:N+1] = 0

    def apply_rbc(self):
        """Apply the reflecting boundary condition, i.e. the surroundig elements
        have the same value as the value on the inside of the boundary.
        """
        N = self.N
        self.states[:, 0    ] = self.states[:, 1]
        self.states[:, N + 1] = self.states[:, N]
        self.states[0, :    ] = self.states[1, :]
        self.states[N + 1, :] = self.states[N, :]

    def apply_pbc(self):
        """Apply the periodic boundary condition.

        This can be viewed as:

        * the square being folded such that opposite ends along each axis
          are glued together. That first gives a tube and then a torus.
        * the square being part of an infinite repetition along each axis
          yielding a periodic pattern.
        """
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

    def evolve(self, n_generations=1, draw=True, stop_if_static=False, curse=None, interval=0.1):
        """Let the system evolve over ``generations`` generations.

        :param int n_generations: the number of generation to evolve.
        :param bool draw: if True, draw each generation on the terminal.
        :param bool stop_if_static: if True stops evolving the system if it is a static state.
        :param float interval: seconds to wait between drawing two successive generations.

        .. note:
            ``stop_if_static`` does not end the evolution when patterns occur that are periodic in
            time. A typical and much occurring time periodic pattern is three live cells in a row
            which alternate being aligned along the X-axis and the Y-axis.
        """
        if self.counts is None:
            self.counts = np.zeros_like(self.states, dtype=int)

        N = self.N
        while n_generations>0:
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
            n_generations -= 1
            # stop if all cells are dead
            if np.sum(self.states) == 0:
                generations = 0
            # stop if fixed state
            if stop_if_static:
                if np.all(previous_states == self.states):
                    generations = 0
            if not curse is None:
                self.curse(curse)
                time.sleep(interval)
            elif draw:
                self.print(boundary=False)


    def print(self, boundary=True, symbols=None):
        """Print this FiniteGrid object to the terminal.

        :param bool boundary: if True, also prints the surrounding boundary layers.
        :param list-like symbols: use ``symbols[0]`` for denoting dead cells, and
            ``symbols[1]`` for denoting living cells in the output. The defaults are
            `` `` and ``X``.
        """
        if symbols:
            self.symbols = symbols
        irange = range(self.N+2) if boundary else range(1,self.N+1)
        jrange = range(self.N+2) if boundary else range(1,self.N+1)
        # print(f'BC = {self.bc}')
        for i in irange:
            s = ''
            for j in jrange:
                s += self.symbols[self.states[i,j]]
            print(s)
        print()

    def curse(self, stdscr, boundary=True, symbols=None):
        """'Print' the FiniteGrid object to the terminal using the Python curses module.

        This gives a nicer visualization because the successive generations are overwriting
        each other, thus being more close to an animation. The current implementation is
        limited to the size of the terminal.

        :param stdscr: the curses wrapper object for the terminal.
        :param bool boundary: if True, also prints the surrounding boundary layers.
        :param list-like symbols: use ``symbols[0]`` for denoting dead cells, and
            ``symbols[1]`` for denoting living cells in the output. The defaults are
            `` `` and ``X``.
        """
        if symbols:
            self.symbols = symbols
        irange = range(self.N+2) if boundary else range(1,self.N+1)
        jrange = range(self.N+2) if boundary else range(1,self.N+1)
        for i in irange:
            s = ''
            for j in jrange:
                s += self.symbols[self.states[i,j]]
            stdscr.addstr(i, 0, s)
        stdscr.addstr(i+1, 0, str(self.generation))
        stdscr.refresh()


    def dump(self,filename='conway'):
        """Pickle this FiniteGrid object (save to file).

        :parameter str filename: name of the pickle file to contain the pickled FiniteGrid object>
        """
        self.counts = None # we do not need to dump counts
        with open(f"{filename}.pickle", mode='wb') as file:
            pickle.dump(self, file=file)
            

    @staticmethod
    def load(filename='conway'):
        """Unpickle a pickled FiniteGrid object.

        :parameter str filename: name of the pickle file containing the pickled FiniteGrid object.
        :return: a FiniteGrid object
        :raises: RuntimeError if unpickling the file does not yield a FiniteGrid object.
        """
        fn = f"{filename}.pickle"
        with open(fn, mode='rb') as file:
            fg = pickle.load(file=file)

        if not isinstance(fg,FiniteGrid):
            raise RuntimeError(f"File '{fn}' does not contain a 'FiniteGrid' object.")

        return fg