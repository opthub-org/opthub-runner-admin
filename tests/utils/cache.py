def test() -> None:
    from traceback import format_exc

    cache = Cache()
    try:
        cache.append({"TrialNo": "1", "Objective": 0.8, "Constraint": None, "Info": {}, "Score": 0.8, "Feasible": True})
    except Exception:
        print(format_exc())
    cache.load("Match#1#Team#1")
    cache.append({"TrialNo": "1", "Objective": 0.8, "Constraint": None, "Info": {}, "Score": 0.8, "Feasible": True})
    cache.load("Match#1#Team#1")
    cache.append({"TrialNo": "2", "Objective": 0.2, "Constraint": None, "Info": {}, "Score": 0.2, "Feasible": False})
    cache.load("Match#1#Team#1")
    cache.append({"TrialNo": "3", "Objective": 0.01, "Constraint": None, "Info": {}, "Score": 0.01, "Feasible": None})
    cache.load("Match#1#Team#2")
    cache.append({"TrialNo": "1", "Objective": 0.3, "Constraint": None, "Info": {}, "Score": 0.3, "Feasible": None})
    cache.load("Match#1#Team#1")
    print(cache.get_values())
    cache.load("Match#1#Team#2")
    print(cache.get_values())
    cache.clear()
    print(cache.get_values())
    cache.load("Match#1#Team#1")
    print(cache.get_values())
    cache.load("Match#1#Team#2")
    cache.clear()
    try:
        cache.append({"TrialNo": "1", "Objective": 0.8, "Constraint": None, "Info": {}, "Score": 0.8, "Feasible": None})
    except Exception:
        print(format_exc())
