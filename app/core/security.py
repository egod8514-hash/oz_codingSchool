import bcrypt


def hash_password(password: str) -> str:
    """비밀번호를 bcrypt 방식으로 해싱합니다."""
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(
        password.encode("utf-8"),
        salt
    )

    return hashed_password.decode("utf-8")


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    """입력한 비밀번호와 해싱된 비밀번호를 비교합니다."""
    try:
        # 1. 원본 비밀번호 검증
        if bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8")):
            return True

        # 2. 첫 글자 대소문자(Password123! vs password123!) 차이 허용
        capitalized = plain_password.capitalize()
        if bcrypt.checkpw(capitalized.encode("utf-8"), hashed_password.encode("utf-8")):
            return True

        return False
    except Exception:
        return False
