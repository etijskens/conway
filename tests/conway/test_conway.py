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
    for i in range(10000):
        print(i)
        fg = cnw.FiniteGrid(3)
        fg.print()
        center_alive = fg.states[2,2]
        center_count = np.sum(fg.states[1:4,1:4]) - fg.states[2,2]
        if center_alive:
            expected = center_count in (2,3)
        else:
            expected = center_count == 3
        print(center_alive, center_count, expected, "=======")
        fg.evolve()
        fg.print()
        assert fg.states[2,2] == expected

def test_evolve1():
    fg = cnw.FiniteGrid(3)
    fg.states[:,:] = 0
    fg.states[1:4,1] = 1
    fg.print()
    center_alive = fg.states[2,2]
    center_count = np.sum(fg.states[1:4,1:4]) - fg.states[2,2]
    if center_alive:
        expected = center_count in (2,3)
    else:
        expected = center_count == 3
    print(center_alive, center_count, expected, "=======")
    fg.evolve()
    fg.print()
    assert fg.states[2,2] == expected

def test_evolve2():
    fg = cnw.FiniteGrid(3)
    fg.states[:,:] = 0
    fg.states[1:4,1:4] = np.array([[0,1,1],[0,1,0],[0,0,1]])
    fg.print()
    center_alive = fg.states[2,2]
    center_count = np.sum(fg.states[1:4,1:4]) - fg.states[2,2]
    if center_alive:
        expected = center_count in (2,3)
    else:
        expected = center_count == 3
    print(center_alive, center_count, expected, "=======")
    fg.evolve()
    fg.print()
    assert fg.states[2,2] == expected



# ==============================================================================
# The code below is for debugging a particular test in eclipse/pydev.
# (otherwise all tests are normally run with pytest)
# Make sure that you run this code with the project directory as CWD, and
# that the source directory is on the path
# ==============================================================================
if __name__ == "__main__":
    the_test_you_want_to_debug = test_evolve

    print("__main__ running", the_test_you_want_to_debug)
    the_test_you_want_to_debug()
    print('-*# finished #*-')

# eof