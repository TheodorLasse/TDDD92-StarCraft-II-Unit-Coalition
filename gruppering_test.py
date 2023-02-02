import random
import time

from modules.gruppering.candidate_solution import UNIT_MAX_VALUE
from modules.gruppering.group_manager import GroupManager, ATTACK, DEFEND

from library import UNIT_TYPEID, Point2D


class DummyUnit:
    """
    A dummy version of the StarCraft II unit object created by IDAbot. Used only for testing.
    """
    def __init__(self, unit_type: int, position: Point2D):
        self.unit_type = unit_type
        self.position = position


class DummyPyUnit:
    """
    A dummy version of the PyUnit object to avoid having to deal with the unit objects created by IDAbot when testing.
    Only used for testing.
    """
    def __init__(self, unit_type: int, position=Point2D()):
        self.unit = DummyUnit(unit_type, position)


def generate_test_group(marines=0, medivacs=0, tanks=0, marauders=0):
    """
    Generates a test group given the amount of units of the different types
    """
    test_group = set()

    for i in range(marines):
        test_group.add(DummyPyUnit(UNIT_TYPEID.TERRAN_MARINE, generate_test_position()))
    for i in range(medivacs):
        test_group.add(DummyPyUnit(UNIT_TYPEID.TERRAN_MEDIVAC, generate_test_position()))
    for i in range(tanks):
        test_group.add(DummyPyUnit(UNIT_TYPEID.TERRAN_SIEGETANK, generate_test_position()))
    for i in range(marauders):
        test_group.add(DummyPyUnit(UNIT_TYPEID.TERRAN_MARAUDER, generate_test_position()))
    return test_group


def generate_test_position() -> Point2D:
    """
    Generates Point2D objects for the tests to use as somewhat realistic positions on the map
    """
    attack_avg_point = Point2D(150, 100)
    defend_avg_point = Point2D(30, 30)

    # About 2/3 of the units should be in the attack army
    is_attack = random.randint(1, 3) != 1

    point_noise_x = random.randint(-20, 20)
    point_noise_y = random.randint(-20, 20)

    if is_attack:
        return attack_avg_point + Point2D(point_noise_x, point_noise_y)
    else:
        return defend_avg_point + Point2D(point_noise_x, point_noise_y)


def run_test_group(test_id: int, gm: GroupManager, test_groups: dict) -> time:
    """
    Runs the test of a given id and prints the results in the terminal
    """
    start_time = time.time()
    gm.update_groups(test_groups.get(test_id))
    end_time = time.time()
    run_time = end_time - start_time

    result = {ATTACK: gm.get_attack_group(), DEFEND: gm.get_defend_group()}

    group_count = {}
    for group in result.keys():
        unit_count = {}
        for py_unit in result.get(group):  # count all the units in the result group
            if py_unit.unit.unit_type in unit_count:
                unit_count[py_unit.unit.unit_type] += 1
            else:
                unit_count[py_unit.unit.unit_type] = 1
        group_count[group] = unit_count

    print("Run time of algorithm: " + str(run_time))
    for i in group_count.keys():
        print(group_count[i])
    print("Value of best found solution: " + str(gm.current_solution.get_value()) + " / " + \
          str(gm.current_solution.length() * UNIT_MAX_VALUE) + "   *Note this is a theoretical max value*")
    print("-------------")

    return run_time


if __name__ == "__main__":

    # marines, medivacs, tanks, marauders
    placement_test = {
        0: generate_test_group(3, 2, 4, 0),
        1: generate_test_group(10, 1, 0, 3),
        2: generate_test_group(20, 4, 5, 10),
        3: generate_test_group(4, 0, 10, 3),
        4: generate_test_group(30, 5, 7, 10)}

    performance_test = {0: generate_test_group(20, 5, 10, 10),
                        1: generate_test_group(20, 5, 10, 10),
                        2: generate_test_group(20, 5, 10, 10),
                        3: generate_test_group(20, 5, 10, 10),
                        4: generate_test_group(20, 5, 10, 10)}

    test_answers = {0: {ATTACK: {UNIT_TYPEID.TERRAN_MARINE: 2, UNIT_TYPEID.TERRAN_MEDIVAC: 1,
                                 UNIT_TYPEID.TERRAN_SIEGETANK: 0, UNIT_TYPEID.TERRAN_MARAUDER: 0},

                        DEFEND: {UNIT_TYPEID.TERRAN_MARINE: 0, UNIT_TYPEID.TERRAN_MEDIVAC: 0,
                                 UNIT_TYPEID.TERRAN_SIEGETANK: 1, UNIT_TYPEID.TERRAN_MARAUDER: 0}},
                    1: {ATTACK: {UNIT_TYPEID.TERRAN_MARINE: 5, UNIT_TYPEID.TERRAN_MEDIVAC: 1,
                                 UNIT_TYPEID.TERRAN_SIEGETANK: 0, UNIT_TYPEID.TERRAN_MARAUDER: 3},

                        DEFEND: {UNIT_TYPEID.TERRAN_MARINE: 3, UNIT_TYPEID.TERRAN_MEDIVAC: 0,
                                 UNIT_TYPEID.TERRAN_SIEGETANK: 0, UNIT_TYPEID.TERRAN_MARAUDER: 0}},
                    2: {ATTACK: {UNIT_TYPEID.TERRAN_MARINE: 16, UNIT_TYPEID.TERRAN_MEDIVAC: 4,
                                 UNIT_TYPEID.TERRAN_SIEGETANK: 0, UNIT_TYPEID.TERRAN_MARAUDER: 8},

                        DEFEND: {UNIT_TYPEID.TERRAN_MARINE: 2, UNIT_TYPEID.TERRAN_MEDIVAC: 0,
                                 UNIT_TYPEID.TERRAN_SIEGETANK: 5, UNIT_TYPEID.TERRAN_MARAUDER: 2}},
                    3: {ATTACK: {UNIT_TYPEID.TERRAN_MARINE: 0, UNIT_TYPEID.TERRAN_MEDIVAC: 0,
                                 UNIT_TYPEID.TERRAN_SIEGETANK: 0, UNIT_TYPEID.TERRAN_MARAUDER: 0},

                        DEFEND: {UNIT_TYPEID.TERRAN_MARINE: 2, UNIT_TYPEID.TERRAN_MEDIVAC: 0,
                                 UNIT_TYPEID.TERRAN_SIEGETANK: 10, UNIT_TYPEID.TERRAN_MARAUDER: 3}},
                    4: {ATTACK: {UNIT_TYPEID.TERRAN_MARINE: 24, UNIT_TYPEID.TERRAN_MEDIVAC: 5,
                                 UNIT_TYPEID.TERRAN_SIEGETANK: 0, UNIT_TYPEID.TERRAN_MARAUDER: 8},

                        DEFEND: {UNIT_TYPEID.TERRAN_MARINE: 4, UNIT_TYPEID.TERRAN_MEDIVAC: 0,
                                 UNIT_TYPEID.TERRAN_SIEGETANK: 7, UNIT_TYPEID.TERRAN_MARAUDER: 2}}}

    gm = GroupManager()
    test_to_run = performance_test

    average_value = 0
    average_time = 0
    for id in range(len(test_to_run)):
        print("Test nr " + str(id + 1))
        average_time += run_test_group(id, gm, test_to_run)
        average_value += gm.current_solution.get_value() / gm.current_solution.length()

    average_value /= len(test_to_run)
    average_time /= len(test_to_run)
    print("Average value: " + str(average_value) + ", Average time: " + str(average_time))
