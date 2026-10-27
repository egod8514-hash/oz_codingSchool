import bcrypt


def hash_password(password: str) -> str:
    """비밀번호를 bcrypt 단방향 해싱합니다."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """평문 비밀번호와 해싱된 비밀번호의 일치 여부를 검증합니다."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False
