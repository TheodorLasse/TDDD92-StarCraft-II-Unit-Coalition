import random
import time

from modules.gruppering.candidate_solution import CandidateSolution, DEFEND, ATTACK
from modules.gruppering.unit_rep import UnitRep
from modules.py_unit import PyUnit


def branch(to_be_branched: CandidateSolution, new_unit: PyUnit, branch_factor: int) -> list[CandidateSolution]:
    branched_candidates = []
    for i in range(branch_factor):
        new_branch = to_be_branched.copy()
        new_branch.add(UnitRep(new_unit.unit.unit_type, i, new_unit.unit.position))

        branched_candidates.append(new_branch)

    return branched_candidates


def pop_random_sample(s: set):
    el = random.sample(s, 1)[0]
    s.remove(el)
    return el


def random_solutions_heuristic(units: set, n: int) -> CandidateSolution:
    """
    Create n random solutions of the units given, return the solution with the highest value
    """
    best_random_candidate = CandidateSolution([])
    for i in range(n):
        units_copy = units.copy()
        unit_rep_list = []
        defend_floor = int(1 / 5 * len(units_copy))
        defend_ceiling = int(3 / 5 * len(units_copy))

        for k in range(random.randint(defend_floor, defend_ceiling)):
            sample_unit = pop_random_sample(units_copy)
            unit_rep_list.append(UnitRep(sample_unit.unit.unit_type, DEFEND, sample_unit.unit.position))

        for k in range(len(units_copy)):
            sample_unit = pop_random_sample(units_copy)
            unit_rep_list.append(UnitRep(sample_unit.unit.unit_type, ATTACK, sample_unit.unit.position))

        random_candidate = CandidateSolution(unit_rep_list)
        random_candidate.update_value()
        if random_candidate.get_value() > best_random_candidate.get_value():
            best_random_candidate = random_candidate

    return best_random_candidate


def branch_and_bound(units: set, branch_factor: int, cancel_time: time) -> CandidateSolution:
    """
    Branch and bound depth first algorithm to find solution of high value. Uses random solutions as heuristic and
    employs preemption to avoid getting stuck with too difficult assignments.
    """
    start_time = time.time()
    iter_counter = 0
    units_list = list(units)

    best_candidate = random_solutions_heuristic(units, 30 * len(units))
    #print("time spent on heuristic: " + str(time.time() - start_time))

    queue = [CandidateSolution([])]

    while len(queue) > 0:
        iter_counter += 1
        if iter_counter % 1000 == 0 and time.time() - start_time > cancel_time:
            #print("took too long... iterations: " + str(iter_counter))
            return best_candidate

        candidate_solution = queue.pop()

        if candidate_solution.length() == len(units):
            # if it's better than current best candidate, replace that candidate, else discard this candidate
            if candidate_solution.get_value() > best_candidate.get_value():
                best_candidate = candidate_solution
                #print("found a better solution!")
        else:
            curr_branch_unit = units_list[candidate_solution.get_next()]
            branched_candidates = branch(candidate_solution, curr_branch_unit, branch_factor)
            for b_candidate in branched_candidates:
                if b_candidate.potential_utility(len(units) - b_candidate.unit_index) > best_candidate.get_value():
                    queue.append(b_candidate)
    #print("iterations: " + str(iter_counter))
    #print(best_candidate.get_groups())
    return best_candidate
