# Caleb Hofschneider SLV ROV 2025

import math
from dataclasses import dataclass
from warnings import deprecated


def diff(a: float, b: float) -> float:
    """
    Gets the difference between two values.

    Args:
        a (float): A number.
        b (float): Another number.

    Returns:
        float: The difference of a and b.
    """

    a = abs(a)
    b = abs(b)
    return max([a, b]) - min([a, b])


def rotate_point(point: tuple, angle: float, form: str='d') -> tuple:
    """
    Rotates a point about the orgin

    Args:
        point (tuple): An (x, y) coordinate tuple.
        angle (float): The rotation angle in degrees or radians.
        form (str): 'd' for an input angle in degrees, 'r' for radians. Default is 'd'.

    Returns:
        tuple: rotated point rounded to 5 decimal places.
    """

    if form == 'd': angle = math.radians(angle)
    elif form != 'r': raise Exception("Invalid form indicator. Supported forms are 'd' (degrees) and 'r' (radians)")

    x, y = point

    # Rotation matrix. Look the term up if you want to understand, but some basic knowledge of linear algebra might be helpful
    x_rotated = round(x * math.cos(angle) - y * math.sin(angle), 5)
    y_rotated = round(x * math.sin(angle) + y * math.cos(angle), 5)

    return (x_rotated, y_rotated)


def adjust_to_linear_range(inpt, from_min, from_max, to_min, to_max):
    from_rng = from_max - from_min
    numerator = inpt - from_min
    percent = numerator / from_rng

    to_rng = to_max - to_min

    return percent * to_rng + to_min


@dataclass
class Circle:
    """
    A class representing a circle defined by its center coordinates and radius.

    Attributes:
        x (float): The x-coordinate of the circle's center.
        y (float): The y-coordinate of the circle's center.
        r (float): The radius of the circle.

    Methods:
        rotate_point_to_other(circle_b: Circle, point: tuple, angle: float, form: str='d') -> tuple: translates a point on this circle to circle_b, rotating by a given angle
    """

    x: float
    y: float
    r: float

    def rotate_point_to_other(self, circle_b, point: tuple, angle: float, form: str='d') -> tuple:
        """
        Transforms a point on circle_a to a corresponding point on circle_b using
        translation, scaling, and rotation.

        Parameters:
            point (tuple): The (x, y) point on circle_a.
            circle_a (Circle): Source circle.
            circle_b (Circle): Destination circle.
            angle (float): rotation angle in degrees or radians.
            form (str): 'd' for an input angle in degrees, 'r' for radians. Default is 'd'.

        Returns:
            tuple: Transformed (x, y) point on circle_b.
        """

        # Explanation:
        #
        # 1: Move the point to be in a circle centered at origin so rotation matrix method in rotate_point can be used
        # 2: Scale the point to match the radius of circle_b
        # 3: Rotate about the origin
        # 4: Translate the point to be centered around the center of circle_b
        #
        # If you don't understand, try visualizing the transformations in Desmos -- if you don't know how to use Desmos, it's a really nice tool

        x, y = point

        x -= self.x
        y -= self.y

        ratio = circle_b.r / self.r
        x *= ratio
        y *= ratio

        rotated = rotate_point((x, y), angle, form)
        x, y = rotated

        x += circle_b.x
        y += circle_b.y

        return (x, y)
    

def clamp_to_circle(point: tuple, circle: Circle) -> tuple:
    """
    Clamps a given point to a given circle.

    Args:
        point (tuple): An (x, y) coordinate tuple.
        circle (Circle): The circle to clamp point to.

    Returns:
        tuple: Clamped (x, y) coordinate rounded to 5 decimal places.
    """

    distance = math.dist(point, (circle.x, circle.y))

    if distance > circle.r:
        x, y = point
        dx, dy = x - circle.x, y - circle.y
        scaler = circle.r / distance
        point = (round(dx * scaler + circle.x, 5), round(dy * scaler + circle.y, 5))

    return point


class Ranged_Int():
    """
    An integer value that is constrained within a defined range [MIN, MAX].

    Attributes:
        MIN (int): The minimum allowable value.
        MAX (int): The maximum allowable value.
        current (int): The current value, always within [MIN, MAX].
    """

    def __init__(self, min: int, max: int, initial: int):
        """
        Initializes a Ranged_Int object with bounds and an initial value.

        NOTE: Adding and subtracting does not return a new Ranged_Int object!

        Args:
            min (int): Minimum allowable value.
            max (int): Maximum allowable value.
            initial (int): Starting value, should be within the range.
        """

        self.MIN = min
        self.MAX = max
        self.current = initial

    def set_value(self, value):
        """
        Sets the current value, clamping it within the defined range.

        Args:
            value (int): The value to set. Will be clamped to [MIN, MAX].
        """

        if value >= self.MIN and value <= self.MAX: self.current = value
        elif value < self.MIN: self.current = self.MIN
        else: self.current = self.MAX

    def __add__(self, other):
        if type(other) in (int, float): return self.current + other
        elif type(other) == type(self): return self.current + other.current

        raise NotImplementedError

    def __sub__(self, other):
        if type(other) in (int, float): return self.current - other
        elif type(other) == type(self): return self.current - other.current
        
        raise NotImplementedError
    
    def __iadd__(self, other):
        sm = self.current + other

        if sm > self.MAX: self.current = self.MAX
        else: self.current = sm
    
        return self

    def __isub__(self, other):
        diff = self.current - other

        if diff < self.MIN: self.current = self.MIN
        else: self.current = diff

        return self

    def __str__(self):
        return f"Min: {self.MIN}, Max: {self.MAX}, Curr: {self.current}"


def map_point_between_circles(point: tuple, circle_a: Circle, circle_b: Circle, angle: float, form: str='d') -> tuple:
    """
    Transforms a point on circle_a to a corresponding point on circle_b using
    translation, scaling, and rotation.

    Parameters:
        point (tuple): The (x, y) point on circle_a.
        circle_a (Circle): Source circle.
        circle_b (Circle): Destination circle.
        angle (float): rotation angle in degrees or radians.
        form (str): 'd' for an input angle in degrees, 'r' for radians. Default is 'd'.

    Returns:
        tuple: Transformed (x, y) point on circle_b.
    """   

    # Explanation:
    #
    # 1: Move the point to be in a circle centered at origin so rotation matrix method in rotate_point can be used
    # 2: Scale the point to match the radius of circle_b
    # 3: Rotate about the origin
    # 4: Translate the point to be centered around the center of circle_b
    #
    # If you don't understand, try visualizing the transformations in Desmos -- if you don't know how to use Desmos, it's a really nice tool

    x, y = point

    x -= circle_a.x
    y -= circle_a.y

    ratio = circle_b.r / circle_a.r
    x *= ratio
    y *= ratio

    rotated = rotate_point((x, y), angle, form)
    x, y = rotated

    x += circle_b.x
    y += circle_b.y

    return (x, y)
