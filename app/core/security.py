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
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False