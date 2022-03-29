"""
Animation using matplotlib.

modified after https://gist.github.com/electronut/5836145
"""

import sys
if not '.' in sys.path:
    sys.path.insert(0,'.')

from conway import FiniteGrid
import matplotlib.pyplot as plt
import matplotlib.animation as animation

N = 200
fg = FiniteGrid(N, boundary='periodic', dump=True)

def update(data):
    fg.evolve(draw=False)
    print(fg.generation)
    mat.set_data(fg.states)
    return [mat]


if __name__ == "__main__":
    # set up animation
    fig, ax = plt.subplots()
    mat = ax.matshow(fg.states)
    ani = animation.FuncAnimation(fig, update, interval=50, save_count=50)
    plt.show()