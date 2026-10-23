import enum

class DepartmentEnum(str, enum.Enum) :
    MEDICAL = "MEDICAL"
    DEV = "DEV"
    RESEARCH = "RESEARCH"