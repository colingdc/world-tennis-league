roles = {
    1: {
        "name": "User",
        "can_manage_tournaments": False,
    },
    2: {
        "name": "Tournament Manager",
        "can_manage_tournaments": True,
    },
    3: {
        "name": "Administrator",
        "can_manage_tournaments": True,
    }
}

tournament_categories = {
    "Test 3 tours": {
        "full_name": "Test 3 tours",
        "number_rounds": 3,
        "points": [100, 50, 20, 5],
    },
    "Grand Chelem": {
        "full_name": "Grand Chelem",
        "number_rounds": 7,
        "points": [2000, 1300, 800, 400, 200, 100, 50, 10],
    },
    "ATP 1000 (7 tours)": {
        "full_name": "ATP 1000 (7 tours)",
        "number_rounds": 7,
        "points": [1000, 650, 400, 200, 100, 50, 25, 10],
    },
    "ATP 1000 (6 tours)": {
        "full_name": "ATP 1000 (6 tours)",
        "number_rounds": 6,
        "points": [1000, 650, 400, 200, 100, 50, 10],
    },
    "ATP 500 (6 tours)": {
        "full_name": "ATP 500 (6 tours)",
        "number_rounds": 6,
        "points": [500, 330, 200, 100, 50, 25, 0],
    },
    "ATP 500 (5 tours)": {
        "full_name": "ATP 500 (5 tours)",
        "number_rounds": 5,
        "points": [500, 330, 200, 100, 50, 0],
    },
    "ATP 250 (6 tours)": {
        "full_name": "ATP 250 (6 tours)",
        "number_rounds": 6,
        "points": [250, 165, 100, 50, 25, 13, 0],
    },
    "ATP 250 (5 tours)": {
        "full_name": "ATP 250 (5 tours)",
        "number_rounds": 5,
        "points": [250, 165, 100, 50, 25, 0],
    },
    "World Tour Finals": {
        "full_name": "World Tour Finals",
        "number_rounds": 3,
        "points": [0, 0, 0, 0],
    },
}
