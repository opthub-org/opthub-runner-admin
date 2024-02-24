# coding: utf-8
"""
The 2-objective sphere function on the 2D euclidean space.
"""
import json


def sphere(x):
    f1 = (x[0] - 1) ** 2 + x[1] ** 2
    f2 = x[0] ** 2 + (x[1] - 1) ** 2
    return [f1, f2]


def main():
    x = input()
    variable = json.loads(x)
    objective = sphere(variable)
    print(json.dumps({"objective": objective, "constraint": None}))


if __name__ == "__main__":
    main()
