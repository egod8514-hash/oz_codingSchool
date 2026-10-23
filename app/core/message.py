from app.core import constants

# 에러 메세지 용 이름
MESSAGE_ITEM_NAME_ID = "유저 ID"
MESSAGE_ITEM_NAME_NAME = "이름"
MESSAGE_ITEM_NAME_AGE = "나이"
MESSAGE_ITEM_NAME_EMAIL = "이메일"
MESSAGE_ITEM_NAME_PASSWORD = "비밀번호"

# 에러 메세지 기본 틀
COMMON_MESSAGE = "{item}은(는) {message}"
COMMON_MESSAGE2 = "{item}이(가) {message}"

# 각종 에러 메세지
MESSAGE_E0001 = "{min} 이상으로 입력해주세요."
MESSAGE_E0002 = "{max} 이하로 입력해주세요."
MESSAGE_E0003 = "{min} 이상, {max} 이하로 입력해주세요."
MESSAGE_E0004 = "{min}자 이상으로 입력해주세요."
MESSAGE_E0005 = "{max}자 이하로 입력해주세요."
MESSAGE_E0006 = "{min}자 이상, {max}자 이하로 입력해주세요."
MESSAGE_E0007 = "영문대문자, 영문소문자, 특수문자가 각각 1개 이상 포함시켜 입력해주세요."
MESSAGE_E0008 = "이메일 형식에 맞게 입력해주세요."
MESSAGE_E0009 = "유효하지 않습니다."
MESSAGE_E0010 = "수정할 데이터(age, email, password)를 전부 입력해주세요."

MESSAGE_ID_RANGE = COMMON_MESSAGE2.format(
    item = MESSAGE_ITEM_NAME_ID,
    message = MESSAGE_E0009
)

MESSAGE_AGE_RANGE = COMMON_MESSAGE.format(
    item = MESSAGE_ITEM_NAME_AGE,
    message = MESSAGE_E0001.format(
        min = constants.MIN_AGE
    )
)

MESSAGE_PASSWORD_REGEX = COMMON_MESSAGE.format(
    item = MESSAGE_ITEM_NAME_PASSWORD,
    message = MESSAGE_E0007
)

MESSAGE_PASSWORD_LEN = COMMON_MESSAGE.format(
    item = MESSAGE_ITEM_NAME_PASSWORD,
    message = MESSAGE_E0006.format(
        min = constants.PASSWORD_MIN_LEN,
        max = constants.PASSWORD_MAX_LEN
    )
)

MESSAGE_EMAIL_REGEX = COMMON_MESSAGE.format(
    item = MESSAGE_ITEM_NAME_EMAIL,
    message = MESSAGE_E0008
)

MESSAGE_EMAIL_LEN = COMMON_MESSAGE.format(
    item = MESSAGE_ITEM_NAME_EMAIL,
    message = MESSAGE_E0005.format(
        max = constants.EMAIL_MAX_LEN
    )
)