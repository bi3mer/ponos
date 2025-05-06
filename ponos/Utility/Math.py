from typing import Tuple
from math import sqrt

def manhattan_distance(a: Tuple[int,...], b: Tuple[int,...]) -> int:
    assert len(a) == len(b)

    distance = 0
    for i in range(len(a)):
        distance += abs(a[i] - b[i])

    return distance

def euclidean_distance(a: Tuple[float,...], b: Tuple[float,...]) -> float:
    assert len(a) == len(b)
    return sqrt(sum((a_ - b_)**2 for a_, b_ in zip(a, b)))

def median(number_list):
    number_list.sort()
    if len(number_list) % 2 == 0:
        median1 = number_list[len(number_list)//2]
        median2 = number_list[len(number_list)//2 - 1]
        return (median1 + median2)/2

    return number_list[len(number_list)//2]

def mean(number_list):
    return sum(number_list) / len(number_list)

def rmse(target, pred):
    assert len(target) == len(pred)
    return sqrt(sum([(t - p)**2 for t , p in zip(target, pred)])/len(target))

def get_slope_and_intercept(x, y):
    sum_x = 0
    sum_y = 0
    sum_x_squared = 0
    sum_xy = 0

    n = len(x)
    for i in range(n):
        x_val = x[i]
        y_val = y[i]

        sum_x += x_val
        sum_x_squared += pow(x_val, 2)
        sum_xy += x_val * y_val
        sum_y += y_val

    # y = mx + b
    denominator  =  ((n * sum_x_squared) - pow(sum_x, 2))
    if denominator == 0:
        return 0, 0

    m = ((n * sum_xy) - (sum_x * sum_y)) / ((n * sum_x_squared) - pow(sum_x, 2))
    b = (sum_y - (m * sum_x)) / n
    return m, b

def tuple_add(a: Tuple[float,...], b: Tuple[float,...]) -> Tuple[float, ...]:
    assert len(a) == len(b)

    return tuple(a[i] + b[i] for i in range(len(a)))

