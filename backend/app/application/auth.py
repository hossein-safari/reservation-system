from app.application.ports import AuthRepository, PasswordHasher, UnitOfWork
from app.domain.entities import Role, User
from app.domain.errors import DomainError


class AuthService:
    def __init__(self, users: AuthRepository, hasher: PasswordHasher, uow: UnitOfWork) -> None:
        self.users = users
        self.hasher = hasher
        self.uow = uow

    def register(self, name: str, email: str, password: str, *, role: Role = Role.CUSTOMER) -> User:
        normalized_email = email.strip().lower()
        if self.users.by_email(normalized_email):
            raise DomainError("email_exists", "This email is already registered.")
        user = User(name.strip(), normalized_email, self.hasher.hash(password), role)
        self.users.add(user)
        self.uow.commit()
        return user

    def authenticate(self, email: str, password: str) -> User:
        user = self.users.by_email(email.strip().lower())
        # Verify a dummy hash as well, so unknown accounts take the password-hashing path.
        hashed = user.password_hash if user else self.hasher.dummy_hash
        valid = self.hasher.verify(password, hashed)
        if not user or not valid:
            raise DomainError("invalid_credentials", "Invalid email or password.", 401)
        return user
