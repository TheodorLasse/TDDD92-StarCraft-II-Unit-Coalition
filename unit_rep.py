from library import Point2D


class UnitRep:
    """
    Represents a unit. Has a unit_type, assigned group and a position
    """
    def __init__(self, unit_type, group: int, position=Point2D()):
        self.unit_type = unit_type
        self.group = group
        self.position = position

    def get_group(self):
        """
        Returns this unit representation's group
        """
        return self.group

    def get_unit_typeID(self):
        """
        Returns this unit's unit_type
        """
        return self.unit_type.unit_typeid

    def copy(self):
        """
        Returns a copy of this unit representation
        """
        return UnitRep(self.unit_type, self.group, self.position)
