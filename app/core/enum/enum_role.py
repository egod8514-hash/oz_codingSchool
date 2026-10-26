import enum

class RoleEnum(str, enum.Enum) : 
    PENDING = "PENDING"
    STAFF = "STAFF"
    ADMIN = "ADMIN"