#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import itertools
import os
import sys
import pprint
from functools import lru_cache

PRINT = 1

pp = pprint.PrettyPrinter(indent=2)
pprint = pp.pprint if PRINT else lambda x: None

TEST_CASES = [
    "a_an_example", "b_better_start_small", "c_collaboration", "d_dense_schedule", "e_exceptional_skills", "f_find_great_mentors"
]

"""
If set, run only that problem number (0=a, 4=e). Set to None otherwise
"""
RUN_ONLY = 0

WRITE = 1


class memoize:
    def __init__(self, func):
        self.func = func
        self.known_keys = []
        self.known_values = []

    def __call__(self, *args, **kwargs):
        key = (args, kwargs)

        if key in self.known_keys:
            i = self.known_keys.index(key)
            return self.known_values[i]
        else:
            value = self.func(*args, **kwargs)
            self.known_keys.append(key)
            self.known_values.append(value)

            return value


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
                filename = "output/{}.dumb.out.txt".format(case)
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
    
    

    pprint(contributors)
    pprint(projects)
    
    print("dumb calculation:")
    answer, _, _ = dumb_assignment(contributors, projects)
    print(len(answer))

    # print("time based calculation:")
    # answer = time_based_assignment(contributors, projects)
    # print(len(answer))

    return answer


"""
Assigns people to projects based on their skills on Day 1, not taking into account skill improvement over time.
Also assigns interns (people with requirement minus one).
"""
def dumb_assignment(contributors, projects):
    skills_to_contributors = {}
    for name, skills in contributors.items():
        for skill, level in skills.items():
            if skill not in skills_to_contributors:
                skills_to_contributors[skill] = []
            skills_to_contributors[skill].append((name, level))
    skills = skills_to_contributors
    print(skills)

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
    return completed_projects, assigned, [p for p in projects if p not in completed_projects]


"""
Assigns people to projects based on their skills on Day 1, not taking into account skill improvement over time.
Also assigns interns (people with requirement minus one).
"""
@memoize
def assignment(contributors, projects):
    skills_to_contributors = {}
    for name, skills in contributors.items():
        for skill, level in skills.items():
            if skill not in skills_to_contributors:
                skills_to_contributors[skill] = []
            skills_to_contributors[skill].append((name, level))
    skills = skills_to_contributors

    completed_projects = []
    all_assigned = []
    for p in sorted(projects, key=lambda x: x["deadline"]):
        assigned = []
        for role in p["roles"]:
            for contributor, level in skills.get(role["name"], []):
                if level >= role["required_level"] and contributor not in assigned and contributor not in all_assigned:
                    role["assigned"] = contributor
                    assigned.append(contributor)
                    break
        # Intern
        for role in p["roles"]:
            if role["assigned"] is not None:
                continue
            intern_found = False
            for contributor, level in skills.get(role["name"], []):
                if intern_found:
                    break
                if level == role["required_level"] - 1 and contributor not in assigned and contributor not in all_assigned:
                    for colleague in assigned:
                        if contributors[colleague].get(role["name"], 0) >= role["required_level"]:
                            role["assigned"] = contributor
                            assigned.append(contributor)
                            intern_found = True
                            break
        if len(assigned) == len(p["roles"]):
            completed_projects.append(p)
            all_assigned.extend(assigned)
        else:
            for role in p["roles"]:
                role["assigned"] = None
    return completed_projects, all_assigned, [p for p in projects if p not in completed_projects]

"""
Assigns people to projects based on time, and then when people are free, assigning them to 
"""
def time_based_assignment(contributors, projects):
    available_people = contributors
    # [ project: x, assigned_time: x, done: false ]
    assignments = []
    all_assigned_projects = []
    time = 0
    no_assignments = False
    while time < 10000:
        if no_assignments and len(assignments) == 0:
            break
        if len(assignments) == 0:
            no_assignments = True
        # if not time % 1000 or time < 10:
        #     print(time, assignments, len(available_people))
        # free up busy people and level them up
        for a in assignments:
            project = a[0]
            assigned_time = a[1]
            if project["duration"] + assigned_time <= time:
                roles = project["roles"]
                for r in roles:
                    name = r["assigned"]
                    skill = r["name"]
                    contributor = contributors[name]
                    if r["required_level"] >= contributor[skill]:
                        contributor[skill] += 1
                    available_people[name] = contributor
                a[2] = True
        assignments = [a for a in assignments if not a[2]]

        # assign all available people at the time
        assigned_projects, assigned, projects = assignment(available_people, projects)
        # print(assigned_projects, assigned, projects)
        all_assigned_projects.extend(assigned_projects)

        new_dict = dict()
        for k, v in available_people.items():
            if k not in assigned:
                new_dict[k] = v
        available_people = new_dict

        for project in assigned_projects:
            assignments.append([project, time, False])
        time += 1

    return all_assigned_projects


def format_answer(answer):
    print("formatting")
    pprint(answer)
    out = []
    out.append(str(len(answer)))
    for project in answer:
        out.append(project["name"])
        out.append(" ".join(role["assigned"] for role in project["roles"]))
    pprint(out)
    return "\n".join(out)

if __name__ == "__main__":
    main()
