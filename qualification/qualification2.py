#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import itertools
import os
import sys
import pprint


PRINT = 1

pp = pprint.PrettyPrinter(indent=2)
pprint = pp.pprint if PRINT else lambda x: None

TEST_CASES = [
    "a_an_example", "b_better_start_small", "c_collaboration", "d_dense_schedule", "e_exceptional_skills", "f_find_great_mentors"
]

"""
If set, run only that problem number (0=a, 4=e). Set to None otherwise
"""
RUN_ONLY = 5

WRITE = 1


def main():
    def process(case, iteration=None):
        print("Case " + case)
        filename = "input_data/{}.in.txt".format(case)
        with open(os.path.join(sys.path[0], filename)) as f:
            case_input = [line.strip("\n") for line in f.readlines()]
            answer = qualification(case_input)
            a = format_answer(answer)
            print("answer:", len(answer))
            if WRITE:
                a = format_answer(answer)
                filename = "output/{}.dumbwithinterns.out.txt".format(case)
                if iteration is not None:
                    filename = "output/batch/{}.{}.out.txt".format(case, t)
                with open(os.path.join(sys.path[0], filename), 'w') as f:
                    f.write(a)

    if RUN_ONLY is not None:
        process(TEST_CASES[RUN_ONLY])
    else:
        for case in TEST_CASES:
            process(case)

    # for t in range(100):
    #     print(t)
    #     case = 3
    #     process(TEST_CASES[case], iteration=t)


def parse_input(case_input):
    num_contributors, num_projects = int(
        case_input[0].split()[0]), int(case_input[0].split()[1])
    i = 1
    contributors = {}
    projects = []
    for _ in range(num_contributors):
        skills = {}
        contributor_name, num_skills = case_input[i].split()
        i += 1
        for _ in range(int(num_skills)):
            skill_name, level = case_input[i].split()
            i += 1
            skills[skill_name] = int(level)
        contributors[contributor_name] = skills

    for _ in range(num_projects):
        project = {}
        roles = []
        name, duration, score, deadline, num_roles = case_input[i].split()
        i += 1
        for _ in range(int(num_roles)):
            role_name, level = case_input[i].split()
            i += 1
            roles.append({"name": role_name, "required_level": int(level), "assigned": None})

        project["name"] = name
        project["duration"] = int(duration)
        project["score"] = int(score)
        project["deadline"] = int(deadline)
        project["roles"] = roles
        projects.append(project)

    return contributors, projects


def qualification(case_input):
    contributors, projects = parse_input(case_input)
    
    skills_to_contributors = {}
    for name, skills in contributors.items():
        for skill, level in skills.items():
            if skill not in skills_to_contributors:
                skills_to_contributors[skill] = []
            skills_to_contributors[skill].append((name, level))

    pprint(contributors)
    pprint(skills_to_contributors)
    # print(projects)
    
    print("dumb calculation:")
    answer = dumb_assignment(contributors, skills_to_contributors, projects)
    # print(answer)

    return answer


"""
Assigns people to projects based on their skills on Day 1, not taking into account skill improvement over time.
Also assigns interns ()
"""
def dumb_assignment(contributors, skills, projects):
    completed_projects = []
    for p in projects:
        assigned = []
        for role in p["roles"]:
            for contributor, level in skills[role["name"]]:
                if level >= role["required_level"] and contributor not in assigned:
                    role["assigned"] = contributor
                    assigned.append(contributor)
                    break
        # Intern
        for role in p["roles"]:
            if role["assigned"] is not None:
                continue
            intern_found = False
            for contributor, level in skills[role["name"]]:
                if intern_found:
                    break
                if level == role["required_level"] - 1 and contributor not in assigned:
                    for colleague in assigned:
                        if contributors[colleague].get(role["name"], 0) >= role["required_level"]:
                            role["assigned"] = contributor
                            assigned.append(contributor)
                            intern_found = True
                            break
        if len(assigned) == len(p["roles"]):
            completed_projects.append(p)
    return completed_projects


def format_answer(answer):
    out = []
    out.append(str(len(answer)))
    for project in answer:
        out.append(project["name"])
        out.append(" ".join(role["assigned"] for role in project["roles"]))
    return "\n".join(out)

if __name__ == "__main__":
    main()
