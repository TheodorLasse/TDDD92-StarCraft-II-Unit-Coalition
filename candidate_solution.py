from modules.gruppering.unit_rep import UnitRep
import math
from itertools import combinations
from library import UNIT_TYPEID, Point2D

ATTACK = 0  # indexes of groups
DEFEND = 1

def clamp(n, min_val, max_val):
    return max(min(max_val, n), min_val)


def dist(p1, p2):
    (x1, y1), (x2, y2) = p1, p2
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)


UNIT_MAX_VALUE = 100

UNIT_TYPES = [UNIT_TYPEID.TERRAN_MARINE, UNIT_TYPEID.TERRAN_MARAUDER, UNIT_TYPEID.TERRAN_MEDIVAC,
              UNIT_TYPEID.TERRAN_SIEGETANK]


def create_unit_dict(units: list[UnitRep]) -> dict:
    """
    Summarizes the information about the units and sorts the information into their respective groups.
    Information includes amount of units of a specific unit type and average distance between units in a group.
    """
    group_dict = {ATTACK: {}, DEFEND: {}}

    for t in UNIT_TYPES:
        group_dict[ATTACK][t] = 0
        group_dict[DEFEND][t] = 0

    for coord in ("x", "y"):
        group_dict[ATTACK][coord] = []
        group_dict[DEFEND][coord] = []

    for unit_rep in units:
        group_dict[unit_rep.group][unit_rep.get_unit_typeID()] += 1
        group_dict[unit_rep.group]["x"].append(unit_rep.position.x)
        group_dict[unit_rep.group]["y"].append(unit_rep.position.y)

    for g in group_dict.keys():
        points = list(zip(group_dict[g].get("x"), group_dict[g].get("y")))
        distances = [dist(p1, p2) for p1, p2 in combinations(points, 2)]
        avg_distance = sum(distances) / max(len(distances), 1)
        group_dict[g]["avg_dist"] = avg_distance

    return group_dict


class CandidateSolution:
    """
    Represents a candidate solution of the branch and bound algorithm. It is a partially assigned solution of the
    problem.
    """
    def __init__(self, units: list[UnitRep], unit_index=0, candidate_value=0):
        self.units = units  # A list of unit representations
        self.candidate_value = candidate_value
        self.unit_index = unit_index

    def add(self, unit: UnitRep) -> None:
        """
        Adds a unit representation to the candidate solution and updates the solution's value
        """
        self.units.append(unit)
        self.candidate_value = self.utility_function()

    def length(self) -> int:
        """
        Returns the amount of units assigned in the candidate solution
        """
        return len(self.units)

    def update_value(self) -> None:
        """
        Updates the value of the candidate solution
        """
        self.candidate_value = self.utility_function()

    def get_groups(self) -> list[list[UnitRep]]:
        """
        Returns the assigned units in their respective groups
        """
        groups = [[], []]
        for unit_rep in self.units:
            groups[unit_rep.get_group()].append(unit_rep.get_unit_typeID())

        return groups

    def get_next(self):
        """
        Returns the index of the next unit to be added to this candidate solution as well as updating the index value
        """
        temp = self.unit_index
        self.unit_index += 1
        return temp

    def get_value(self) -> float:
        """
        Returns the value of this candidate solution
        """
        return self.candidate_value

    def get_units(self) -> list[UnitRep]:
        """
        Returns a list of unit representations of the assigned units of this candidate solution
        """
        return self.units.copy()

    def copy(self):
        """
        Returns a copy of this candidate solution
        """
        return CandidateSolution(self.get_units(), self.unit_index, self.candidate_value)

    def utility_function(self) -> float:
        """
        Returns an approximated value of this candidate solution's distribution of units. Based on notions found online
        by players much better than me, such as the rule of thumb of one medivac for every 8 marines or 4 marauders.
        It also accounts for distance between units as to avoid grouping units that are too far apart together.
        """

        group_dict = create_unit_dict(self.units)
        non_penalized_dist = 50

        # Attack group value
        attack_group = group_dict.get(ATTACK)
        marines = attack_group.get(UNIT_TYPES[0])
        marauders = attack_group.get(UNIT_TYPES[1])
        medivacs = attack_group.get(UNIT_TYPES[2])
        tanks = attack_group.get(UNIT_TYPES[3])

        medivacs_needed = marines / 8 + marauders / 4
        medivac_efficiency = clamp(medivacs / max(medivacs_needed, 0.25), 0.4, 1)
        living_unit_utility = medivac_efficiency * (marines + marauders + medivacs)
        tank_unit_utility = tanks * 0.75

        distance_penalty = clamp(non_penalized_dist / max(attack_group.get("avg_dist"), 1), 0.5, 1)

        modifiers = UNIT_MAX_VALUE * distance_penalty
        attack_utility = (living_unit_utility + tank_unit_utility) * modifiers

        # Defend group value
        defend_group = group_dict.get(DEFEND)
        marines = defend_group.get(UNIT_TYPES[0])
        marauders = defend_group.get(UNIT_TYPES[1])
        medivacs = defend_group.get(UNIT_TYPES[2])
        tanks = defend_group.get(UNIT_TYPES[3])

        medivacs_needed = marines / 8 + marauders / 4
        medivac_efficiency = clamp(medivacs / max(medivacs_needed, 0.25), 0.4, 1)

        defend_sum = marines + marauders + medivacs + tanks
        # Anything larger than 1/3 of the total amount of units in defend group is penalized
        defend_size_weight = clamp(min(len(self.units) / max(defend_sum * 3, 1), 1), 0, 1)

        living_unit_utility = medivac_efficiency * (marines + marauders + medivacs)

        distance_penalty = clamp(non_penalized_dist / max(defend_group.get("avg_dist"), 1), 0.5, 1)

        modifiers = defend_size_weight * UNIT_MAX_VALUE * distance_penalty
        defend_utility = (living_unit_utility + tanks) * modifiers

        return attack_utility + defend_utility

    def potential_utility(self, units_left) -> float:
        """
        The bound of this candidate solution. In theory, it gives a ceiling on the potential value of this candidate
        solution, but in practice units may retroactively gain value through additions to the group. For example a
        marine may gain value through the addition of a medivac unit.
        """
        # The bound function below would be more optimistic, not sure if it's any better though, need to flesh out
        # other parts of the code before I can find out for sure, until then I use the conservative function.
        # return units_left * UNIT_MAX_VALUE + clamp(self.candidate_value * 1.25, 0, len(self.units) * UNIT_MAX_VALUE)
        return units_left * UNIT_MAX_VALUE + self.candidate_value
