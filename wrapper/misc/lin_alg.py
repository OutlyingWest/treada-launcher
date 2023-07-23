from typing import List, Union, Tuple, Any
import warnings

import numpy as np


# Enable runtime warnings ignore mode
warnings.filterwarnings('ignore', category=RuntimeWarning)

a = np.array([0,0,0])
a.nonzero()


def line_coefficients(first_point_coords: List[Union[int, float]],
                      second_point_coords: List[Union[int, float]]) -> Tuple[Any, Any]:
    x1, y1 = first_point_coords
    x2, y2 = second_point_coords
    # Set coefficients of A matrix
    A = np.array([[x1, 1],
                  [x2, 1]])
    # Set right side coefficients - Y vector
    Y = np.array([y1, y2])
    # Solve linear system
    k, b = np.linalg.solve(A, Y)
    return k, b


def lines_intersection(coefficients_1: list, coefficients_2: list) -> tuple:
    k1, b1 = coefficients_1
    k2, b2 = coefficients_2
    A = np.array([[k1, -1],
                  [k2, -1]])
    Y = np.array([-b1, -b2])
    # Solve linear system
    x, y = np.linalg.solve(A, Y)
    return x, y


def extend_line(x_coords: list, y_coords: list, line_length=None) -> Tuple[list, list]:
    x1, x2 = x_coords
    y1, y2 = y_coords
    k, b_coef = line_coefficients([x1, y1], [x2, y2])
    if line_length is None:
        line_length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    x_plus = x2 + line_length
    y_plus = k * x_plus + b_coef
    x_minus = x1 - line_length
    y_minus = k * x_minus + b_coef
    return [x_minus, x_plus], [y_minus, y_plus]


def find_angle(k1, k2, degrees=False):
    tg = np.abs((k2 - k1) / (1 + k1 * k2))
    print(f'{tg=}')
    angle_rad = np.arctan(tg)
    if not degrees:
        return angle_rad
    else:
        return np.degrees(angle_rad)


if __name__ == '__main__':
    import matplotlib
    matplotlib.use('TkAgg')
    import matplotlib.pyplot as plt

    X = np.linspace(0, 5, 6)
    print(X)

    # Line 1
    k1, b1 = line_coefficients([-1, 1], [5, 3])
    print(f'line 1: {k1=} {b1=}')
    Y1 = k1*X + b1

    # Line 2
    k2, b2 = line_coefficients([-3, -1], [1, 10])
    print(f'line 2: {k2=} {b2=}')
    Y2 = k2*X + b2

    # Find angle
    angle = find_angle(k1, k2, degrees=True)
    print(f'{angle=}')

    # Find intersection
    x_in, y_in = lines_intersection([k1, b1], [k2, b2])
    print(f'{x_in=} {y_in=}')

    # Plotting
    fig, ax = plt.subplots()

    # Plot lines
    ax.plot(X, Y1, color='red', label='Line 1')
    ax.plot(X, Y2, color='blue', label='Line 2')

    # Plot intersection point
    ax.scatter(x_in, y_in, color='black', zorder=2, label='Inters. point')
    plt.annotate(xy=(x_in, y_in), text=f'{x_in},{y_in}')

    # Settings
    ax.legend()
    ax.grid(True)
    # ax.set_aspect('equal')
    plt.xlim(-5, 5)
    plt.ylim(-5, 5)


    plt.show()

