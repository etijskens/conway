import sys
if not '.' in sys.path:
    sys.path.insert(0,'.')
    
from conway import FiniteGrid

if __name__ == "__main__":
    N = 20
    fg = FiniteGrid(N)
    fg.print(boundary=False,symbols=' x')
    fg.evolve(500, stop_if_static=True)