from passlib.context import CryptContext

pwd_context = CryptContext(schemes = ["bcrypt"], deprecated = "auto")

# 비밀번호 확인
def verify_password(
            plain_password : str,
            hashed_password : str
    ) -> bool : 

    return pwd_context.verify(plain_password, hashed_password)

# 패스워드 변경 시 해시코드로 변경
def get_password_hash(
            password : str
    ) -> str : 

    return pwd_context.hash(password)