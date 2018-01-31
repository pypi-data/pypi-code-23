"""
.. module:: coordinate
    :synopsis: Axial and cube coordinates for hexagons

.. moduleauthor:: Diorge Brognara <diorge.bs@gmail.com>

Special thanks to Amit and his post: http://www.redblobgames.com/grids/hexagons
"""


import sys
from itertools import permutations


class Cube:
    """Cube coordinates for a hexagon

    The coordinates (x, y, z) represent an unique hexagon
    .. note:: x + y + z = 0 (or very close to it, there's some tolerance)
    """

    TOLERANCE = 0.5

    def __init__(self, x, y, z):
        """Creates a new immutable cube coordinate from points x, y, z

        :param x: X coordinate
        :type x: int or float
        :param y: Y coordinate
        :type y: int or float
        :param z: Z coordinate
        :type z: int or float

        .. note:: Many operations assume the coordinates to be int,
                  you may wish to use :func:`Cube.round` before you apply
                  these operations.
        """
        if abs(x + y + z) > Cube.TOLERANCE:
            raise ValueError(f'Cube ({x}, {y}, {z}) does not slice the x+y+z=0 plane')
        self._x = x
        self._y = y
        self._z = z

    @property
    def x(self):
        """Read-only X coordinate of the cube
        :returns: int or float -- the X coordinate
        """
        return self._x

    @property
    def y(self):
        """Read-only Y coordinate of the cube
        :returns: int or float -- the Y coordinate
        """
        return self._y

    @property
    def z(self):
        """Read-only Z coordinate of the cube
        :returns: int or float -- the Z coordinate
        """
        return self._z

    def to_axial(self):
        """Converts the cube coordinate to an axial coordinate
        :returns: Axial -- the unique corresponding axial coordinate
        """
        return Axial(self.x, self.z)

    def neighbors(self):
        """The neighbor cubes of the cube, assuming infinite grid

        Always returns six neighbors in the same order (which is right border
        first, then counterclock-wise).

        :returns: iterable of Cube -- the neighbors
        """
        return map(lambda d: self + d, Cube._neighbor_directions)

    def diagonals(self):
        """The coordinates of the six diagonal hexagons

        Diagonals are connected by a single edge, but no borders,
        so the diagonals are distance 2 apart from the center

        :returns: iterable of Cube -- the diagonals
        """
        return map(lambda d: self + d, Cube._diagonal_directions)

    def distance(self, other):
        """Calculates the distance between two hexagons

        The distance is the number of hexes needed to traverse
        to get from one point to the other

        :returns: int or float
        """
        return max(abs(self.x - other.x), abs(self.y - other.y),
                   abs(self.z - other.z))

    def round(self):
        """Rounds a floating point to the nearest hexagon

        This is not the same as rounding every coordinate,
        because of the x+y+z=0 restriction.

        Use this method when dealing with fractional cubes,
        for example conversions to/from pixels.

        :returns: Cube -- a new Cube coordinate with int values
        """
        rx, ry, rz = map(round, self)
        dx, dy, dz = [abs(d - o) for (d, o) in zip((rx, ry, rz), self)]
        if dx > dy and dx > dz:
            rx = -(ry + rz)
        elif dy > dz:
            ry = -(rx + rz)
        else:
            rz = -(rx + ry)
        return Cube(rx, ry, rz)

    def line_to(self, target):
        """Returns all hexes in a straight-line

        The result is in order from self to target,
        both extremes included.

        :param target: end of the line
        :type target: Cube
        :returns: iterable of Cube -- points in the line
        """
        def lerp(a, b, t):
            return a + (b - a) * t

        def cube_lerp(a, b, t):
            return Cube(*(lerp(ax, bx, t) for (ax, bx) in zip(a, b)))

        n = self.distance(target)
        for i in range(n + 1):
            yield (cube_lerp(self, target, i / n) + Cube._epsilon).round()

    def circle_around(self, size, obstacles=None):
        """The collection of hexagons in a circle around this

        :param size: the maximum distance, or radius of the circle
        :type size: int
        :param obstacles: function returning True for obstacle coordinates,
                          see :func:`Cube.floodfill`
        :type obstacles: callable
        :returns: iterable of Cube -- collection of hexagons in the circle
        """
        if obstacles is not None:
            yield from self.floodfill(size, obstacles)
        else:
            for x in range(-size, size + 1):
                start = max(-size, -x - size)
                end = min(size, -x + size)
                for y in range(start, end + 1):
                    z = -(x + y)
                    yield self + Cube(x, y, z)

    def floodfill(self, size, obstacle):
        """The collection of hexagons reachable in a finite amount of steps

        Performs a flood-fill, collecting every reachable hexagon,
        as long as no more than size steps are taken.
        Will not walk through hexagons for which obstacle returns True.

        :param size: the maximum number of steps from the origin
        :type size: int
        :param obstacle: function returning True for obstacle coordinates
        :type obstacle: callable
        :returns: iterable of Cube -- collection of reachable hexagons
        """
        visited = set([self])
        reachable = [[self]]

        for k in range(1, size + 1):
            reachable.append([])
            for cube in reachable[k - 1]:
                neighbors = cube.neighbors()
                for neighbor in neighbors:
                    if neighbor not in visited and not obstacle(neighbor):
                        visited.add(neighbor)
                        reachable[k].append(neighbor)
        return visited

    def rotate_right(self, center=None, amount=1):
        """Returns the point after rotating to the right

        Makes an amount of 60 degree rotations to the right,
        centered in some other point (defaults to origin).

        :param center: rotation center
        :type center: Cube
        :param amount: amount of 60 degree rotations
        :type amount: int
        :returns: Cube -- point after rotation
        """
        if center is None:
            center = Cube.origin
        point = self - center
        for i in range(amount):
            x, y, z = point
            point = Cube(-z, -x, -y)
        return point + center

    def rotate_left(self, center=None, amount=1):
        """Returns the point after rotating to the left

        Makes an amount of 60 degree rotations to the left,
        centered in some other point (defaults to origin).

        :param center: rotation center
        :type center: Cube
        :param amount: amount of 60 degree rotations
        :type amount: int
        :returns: Cube -- point after rotation
        """
        if center is None:
            center = Cube.origin
        point = self - center
        for i in range(amount):
            x, y, z = point
            point = Cube(-y, -z, -x)
        return point + center

    def circumference(self, radius):
        """Returns the circumference around this point

        :param radius: the fixed distance from the center
        :type radius: int
        :returns: iterable of Cube -- the ring
        """
        current = set()
        first = radius
        for second in range(-radius, 1):
            third = -(first + second)
            for perm in permutations([first, second, third]):
                current.add(self + Cube(*perm))
        first = -radius
        for second in range(0, radius + 1):
            third = -(first + second)
            for perm in permutations([first, second, third]):
                current.add(self + Cube(*perm))
        return current

    def arc(self, direction, size):
        """Returns the arc within a 120 degree vision

        :param direction: facing direction from self (a neighbor)
        :type direction: Cube
        :param size: size of the ring
        :type size: int
        :returns: iterable of Cube -- visible members of the arc
        """
        horizon = (direction - self) * size
        left_horizon = horizon.rotate_left(self)
        right_horizon = horizon.rotate_right(self)
        left_line = set(left_horizon.line_to(horizon))
        right_line = set(right_horizon.line_to(horizon))
        return left_line | right_line

    def __add__(self, other):
        """Coordinate-wise addition

        :param other: coordinate to be added
        :type other: Cube
        :returns: Cube -- the resulting addition
        """
        return Cube(self.x + other.x, self.y + other.y, self.z + other.z)

    def __neg__(self):
        """Negates all coordinates

        :returns: Cube -- the opposing cube
        """
        return Cube(-self.x, -self.y, -self.z)

    def __sub__(self, other):
        """Coordinate-wise subtraction

        :param other: coordinate to be subtracted from self
        :type other: Cube
        :returns: Cube -- the resulting subtraction
        """
        return self + (-other)

    def __mul__(self, scalar):
        """Scalar multiplication

        :param scalar: the scalar value
        :type scalar: int or float
        :returns: Cube -- scaled coordinate
        """
        return Cube(self.x * scalar, self.y * scalar, self.z * scalar)

    def __eq__(self, other):
        """Determines equality

        :param other: object to be compared
        :type other: Cube
        :returns: bool -- True if equal and False otherwise
        """
        return (self.x, self.y, self.z) == (other.x, other.y, other.z)

    def __hash__(self):
        """Hash value

        :returns: int -- hash value
        """
        return hash(tuple(self.__iter__()))

    def __repr__(self):
        """Debugging representation

        :returns: str -- readable representation
        """
        return 'Cube({x}, {y}, {z})'.format(x=self.x, y=self.y, z=self.z)

    def __iter__(self):
        """Iterable of the coordinates

        :returns: iterable of int or float -- the coordinates
        """
        yield self.x
        yield self.y
        yield self.z

Cube.origin = Cube(0, 0, 0)
Cube._neighbor_directions = (Cube(1, -1, 0), Cube(1, 0, -1), Cube(0, 1, -1),
                             Cube(-1, 1, 0), Cube(-1, 0, 1), Cube(0, -1, 1))
Cube._diagonal_directions = (Cube(2, -1, -1), Cube(1, 1, -2), Cube(-1, 2, -1),
                             Cube(-2, 1, 1), Cube(-1, -1, 2), Cube(1, -2, 1))
Cube._epsilon = Cube(sys.float_info.epsilon, sys.float_info.epsilon,
                     -2 * sys.float_info.epsilon)


class Axial:
    """Axial coordinates for a hexagon

    Delegates most operations to :class:`Cube`,
    convert when needed. Axial coordinates are better
    for storage and pixel conversions
    """

    def __init__(self, q, r):
        self._q = q
        self._r = r

    @property
    def q(self):
        """Column coordinate
        """
        return self._q

    @property
    def r(self):
        """Row coordinate
        """
        return self._r

    def to_cube(self):
        """Converts the axial coordinate to a cube coordinate

        :returns: Cube -- equivalent unique cube coordinate representation
        """
        return Cube(self.q, -(self.q + self.r), self.r)

    def neighbors(self):
        """The neighbor hexagons, assuming infinite grid

        :returns: iterable of Axial -- the neighbors
        """
        return(map(lambda d: Axial(self.q + d.q, self.r + d.r),
                   Axial._neighbor_directions))

    def __eq__(self, other):
        return (self.q, self.r) == (other.q, other.r)

    def __add__(self, other):
        return Axial(self.q + other.q, self.r + other.r)

    def __neg__(self):
        return Axial(-self.q, -self.r)

    def __sub__(self, other):
        return self + (-other)

    def __repr__(self):
        return 'Axial({q}, {r})'.format(q=self.q, r=self.r)

    def __iter__(self):
        yield self.q
        yield self.r

    def __hash__(self):
        return hash(self.to_cube())

Axial._neighbor_directions = tuple(map(Cube.to_axial,
                                       Cube._neighbor_directions))
