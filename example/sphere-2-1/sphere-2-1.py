# coding: utf-8
"""
The single-objective sphere function on the 2D euclidean space.
"""
import json


def sphere(variable):
    return sum(x**2 for x in variable)


def main():
    x = input()
    variable = json.loads(x)
    objective = sphere(variable)
    print(json.dumps({"objective": objective, "constraint": None}))


if __name__ == "__main__":
    main()
