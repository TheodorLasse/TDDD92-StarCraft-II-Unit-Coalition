from modules.gruppering.branch_and_bound import branch_and_bound
from modules.gruppering.candidate_solution import ATTACK, DEFEND
from modules.py_unit import PyUnit

NR_OF_GROUPS = 2


class GroupManager:
    """
    Manages the three different groups of attack, defend and scout
    """
    def __init__(self):
        self.units = []
        self.current_solution = None
        self.time_limit = 10
        for i in range(NR_OF_GROUPS):
            self.units.append([])

    def update_groups(self, units: set[PyUnit]) -> None:
        """
        Update the groups given a set of PyUnits
        """
        self.current_solution = branch_and_bound(units, NR_OF_GROUPS, self.time_limit)

        groups = [[], [], []]

        unit_rep_list = self.current_solution.get_units()
        for unit_rep in unit_rep_list:
            for py_unit in units:
                if unit_rep.position == py_unit.unit.position and unit_rep.unit_type == py_unit.unit.unit_type:
                    groups[unit_rep.get_group()].append(py_unit)
                    continue

        self.units = groups

    def get_attack_group(self) -> list:
        """
        Returns the attack group
        """
        return self.units[ATTACK]

    def get_defend_group(self) -> list:
        """
        Returns the defend group
        """
        return self.units[DEFEND]
