# -*- coding: utf-8 -*-

"""Tests for conway package."""

import sys

import numpy as np

sys.path.insert(0,'.')

import conway as cnw


def test_FiniteGrid():
    fg = cnw.FiniteGrid()
    for bc in cnw.FiniteGrid.boundary_conditions:
        fg.apply_bc(bc)
        fg.print()
        N = fg.N
        s = fg.states
        for i in range(N + 2):
            for j in range(N + 2):
                if i in (0 ,N+1) and j in (0, N+1): # a boundary cell
                    if bc == 'zero':
                        assert s[i,j] == 0
                    else:
                        if bc == 'reflect':
                            i0 = 1 if (i == 0) else N
                            j0 = 1 if (j == 0) else N
                        else:  # 'periodic'
                            i0 = N if (i == 0) else 1
                            j0 = N if (j == 0) else 1
                        assert s[i,j] == s[i0,j0]
                else:
                    assert fg.states[i,j] in (0,1)


def test_evolve():
    for i in range(100000):
        print(i)
        fg = cnw.FiniteGrid(3)
        fg.print(boundary=False)
        center_alive = fg.states[2,2]
        center_count = np.sum(fg.states[1:4,1:4]) - fg.states[2,2]
        if center_alive:
            expected = center_count in (2,3)
        else:
            expected = center_count == 3
        print(center_alive, center_count, expected, "=======")
        fg.evolve()
        fg.print(boundary=False)
        assert fg.states[2,2] == expected


def test_evolve1():
    fg = cnw.FiniteGrid(3)
    fg.states[:,:] = 0
    fg.states[1:4,1] = 1
    fg.print(boundary=False)
    center_alive = fg.states[2,2]
    center_count = np.sum(fg.states[1:4,1:4]) - fg.states[2,2]
    if center_alive:
        expected = center_count in (2,3)
    else:
        expected = center_count == 3
    print(center_alive, center_count, expected, "=======")
    fg.evolve()
    fg.print(boundary=False)
    assert fg.states[2,2] == expected


def test_evolve2():
    fg = cnw.FiniteGrid(3)
    fg.states[:,:] = 0
    fg.states[1:4,1:4] = np.array([[0,1,1],[0,1,0],[0,0,1]])
    fg.print(boundary=False)
    center_alive = fg.states[2,2]
    center_count = np.sum(fg.states[1:4,1:4]) - fg.states[2,2]
    if center_alive:
        expected = center_count in (2,3)
    else:
        expected = center_count == 3
    print(center_alive, center_count, expected, "=======")
    fg.evolve()
    fg.print(boundary=False)
    assert fg.states[2,2] == expected

def test_pdraw():
    fg = cnw.FiniteGrid(6)
    fg.pdraw(boundary=False)
    fg.pdraw(boundary=False)
    fg.print(boundary=False)

    fg.pdraw(boundary=True)
    fg.pdraw(boundary=True)
    fg.print(boundary=True)

def test_pdraw_evolve():
    fg = cnw.FiniteGrid(6)
    fg.pdraw(boundary=False)
    fg.evolve(100)

def test_dump():
    filename = 'conway.test'
    fg0 = cnw.FiniteGrid(10)
    fg0.dump(filename=filename)
    fg1 = cnw.FiniteGrid(load=True, filename=filename)
    assert fg0.N == fg1.N
    assert fg0.n == fg1.n
    assert fg0.bc == fg1.bc
    assert np.all(fg0.states == fg1.states)


# ==============================================================================
# The code below is for debugging a particular test in eclipse/pydev.
# (otherwise all tests are normally run with pytest)
# Make sure that you run this code with the project directory as CWD, and
# that the source directory is on the path
# ==============================================================================
if __name__ == "__main__":
    the_test_you_want_to_debug = test_dump

    print("__main__ running", the_test_you_want_to_debug)
    the_test_you_want_to_debug()
    print('-*# finished #*-')

# eof