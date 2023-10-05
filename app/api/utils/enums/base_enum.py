from enum import Enum


class BaseENUM(Enum):
    @classmethod
    def _missing_(cls, value):
        for member in cls:
            if isinstance(value, str) and member.value == value.upper():
                return member

    @classmethod
    def keys(cls):
        """Returns a list of all the enum keys."""
        return cls._member_names_

    @classmethod
    def values(cls):
        """Returns a list of all the enum values."""
        return list(cls._value2member_map_.keys())
