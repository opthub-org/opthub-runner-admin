# coding: utf-8
"""
Best fitness value.
"""
import json


def main():
    solution_to_score = json.loads(input())
    solutions_scored = json.loads(input())
    y = solution_to_score["objective"]
    best = solutions_scored[-1]["score"]
    score = min(y, best)
    print(score)


if __name__ == "__main__":
    main()