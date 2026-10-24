from enum import Enum

class Gender(str, Enum):
    M = "M"
    F = "F"

class Department(str, Enum):
    MEDICAL = "MEDICAL"
    DEV = "DEV"
    RESEARCH = "RESEARCH"

class Role(str, Enum):
    PENDING = "PENDING"
    STAFF = "STAFF"
    ADMIN = "ADMIN"