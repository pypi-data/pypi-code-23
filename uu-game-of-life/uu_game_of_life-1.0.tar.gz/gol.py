import numpy as np
from matplotlib import pyplot as plt
from scipy.ndimage import convolve


def cross(size):
    # add 2 to handle boarders #
    s = np.zeros([size, size])
    c = int(size / 2 - 1)
    s[:, c - 1:c + 2] = 1
    s[c - 1:c + 2, :] = 1

    # pad boarders #
    s[:, 0] = 0
    s[:, size - 1] = 0
    s[0, :] = 0
    s[size - 1, :] = 0

    return s


def r_pentomino(size):
    board = np.zeros([size, size])
    r_pentomino = np.array([[0, 1, 1],
                            [1, 1, 0],
                            [0, 1, 0]])

    c = int(size / 2)
    board[c:c + 3, c:c + 3] = r_pentomino

    return board



def progress(board):
    kernel = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]])
    c = convolve(board, kernel, mode='constant')

    a = (1 - board) * c
    a[a != 3] = 0
    a[a == 3] = 1

    b = board * c
    b[np.where(np.logical_or(b < 2, b > 3))] = 0
    b[b != 0] = 1

    return a + b


def animate_gol(board, nr_of_time_steps):
    import matplotlib.animation as animation

    fig = plt.figure()
    plt.axis('off')

    states = []
    for i in range(nr_of_time_steps):
        states.append((plt.imshow(board, cmap='Purples'),))
        board = progress(board)

    ani = animation.ArtistAnimation(fig, states, interval=20, repeat_delay=10,
                                    blit=True)

    plt.show()


def main():
    board = r_pentomino(100)
    animate_gol(board, 1000)


if __name__ == "__main__":
    main()
