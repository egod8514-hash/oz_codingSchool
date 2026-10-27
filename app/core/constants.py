import re

COL_NAME_ID = "id"
COL_NAME_NAME = "name"
COL_NAME_AGE = "age"
COL_NAME_EMAIL = "email"
COL_NAME_PASSWORD = "password"

MIN_AGE = 14
PHONE_NUMBER_REGEX = re.compile(r"^(01[0-9]|02|0[3-9][0-9])-([0-9]{3,4})-([0-9]{4})$")
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]\.[a-zA-Z]{2,}$")
EMAIL_MAX_LEN = 30
PASSWORD_REGEX = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$")
PASSWORD_MIN_LEN = 8
PASSWORD_MAX_LEN = 20

PARAM_NAME_STATUS_CODE = "status_code"
PARAM_NAME_DETAIL = "detail"

TABLE_NAME_USERS = "users"
TABLE_NAME_XRAY = "xray_images"
TABLE_NAME_MEDICAL = "medical_records"
TABLE_NAME_AI_RESULTS = "ai_analysis_results"
TABLE_NAME_PATIENTS = "patients"

RELATION_CASCADE = "all, delete-orphan"