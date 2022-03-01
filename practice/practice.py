#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import itertools
import os
import sys


TEST_CASES = [
    "a_an_example", "b_basic", "c_coarse", "d_difficult", "e_elaborate"
]

"""
How many test cases to run. 
e.g. 1 runs case a only, 2 runs cases a and b, etc.
"""
NUM_CASES = 5


"""
If set, run only that problem number (0=a, 4=e). Set to None otherwise
"""
RUN_ONLY = 4

WRITE = True

def main():
    def process(case, iteration=None):
        print("Case", case)
        filename = "input_data/{}.in.txt".format(case)
        with open(os.path.join(sys.path[0], filename)) as f:
            case_input = [line.strip("\n") for line in f.readlines()]
            answer = pizza(case_input)
            if WRITE:
                l = len(answer)
                c = [str(l)] + answer
                a = " ".join(c)
                filename = "output/{}.counter.out.txt".format(case)
                if iteration is not None:
                    filename = "output/batch/{}.{}.out.txt".format(case, t)
                with open(os.path.join(sys.path[0], filename), 'w') as f:
                    f.write(a)

    # if RUN_ONLY is not None:
    #     process(TEST_CASES[RUN_ONLY])
    # else:
    #     for case in TEST_CASES[:NUM_CASES]:
    #         process(case)
    
    for t in range(100):
        print(t)
        case = 3
        process(TEST_CASES[case], iteration=t)


def get_clients(case_input):
    clients = []
    all_ingredients = set()
    num_clients, case_input = int(case_input[0]), case_input[1:]
    for i in range(num_clients):
        likes = case_input[i*2].split()[1:]
        dislikes = case_input[i*2+1].split()[1:]
        all_ingredients.update(likes)
        all_ingredients.update(dislikes)
        clients.append([set(likes), set(dislikes)])
    return clients, all_ingredients


def pizza(case_input):
    clients, all_ingredients = get_clients(case_input)
    answer = naive_counter(clients, all_ingredients)
    return answer


def brute_force(clients, all_ingredients):
    best = 0
    best_choices = []

    combinations = []
    for i in range(1, len(all_ingredients)+1):
        combinations.extend(list(x) for x in itertools.combinations(all_ingredients, i))

    for choices in combinations:
        s = score(clients, choices)
        if s > best:
            best = s
            best_choices = choices
    print(best)
    return list(best_choices)

def naive_counter(clients, all_ingredients):
    best = 0
    best_choices = []
    besti = 0

    ingredient_scores = {}
    for ingredient in all_ingredients:
        ingredient_score = 0
        for likes, dislikes in clients:
            if ingredient in likes:
                ingredient_score += 1
            if ingredient in dislikes:
                ingredient_score -= 1
        ingredient_scores[ingredient] = ingredient_score
    
    ranked_ingredients = sorted(ingredient_scores, key=ingredient_scores.get, reverse=True)
    # print({i: ingredient_scores[i] for i in ranked_ingredients})
    # print(ranked_ingredients)
    for i in range(1, len(ingredient_scores) + 1):
        s = score(clients, ranked_ingredients[:i])
        if s > best:
            best = s
            besti = i
            best_choices = ranked_ingredients[:i]
    print(best,)
    return list(best_choices)

def score(clients, chosen_ingredients):
    happy_clients = 0
    chosen_ingredients = set(chosen_ingredients)
    for likes, dislikes in clients:
        if likes.issubset(chosen_ingredients) and dislikes.isdisjoint(chosen_ingredients):
            happy_clients += 1
    return happy_clients


if __name__ == "__main__":
    main()
