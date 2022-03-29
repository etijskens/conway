from conway import FiniteGrid

if __name__ == "__main__":
    N = 20
    fg = FiniteGrid(N)
    fg.pdraw2(boundary=False)
    fg.evolve(500, stop_if_static=True)