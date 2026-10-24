from app.application.commands.register_user import RegisterUserCommand
from app.application.dto.authenticated_session import AuthenticatedSession
from app.application.ports.password_hasher import PasswordHasher
from app.application.ports.token_codec import TokenCodec
from app.application.ports.unit_of_work import UnitOfWork
from app.application.ports.user_repository import UserRepository
from app.domain.entities.user import Role, User
from app.domain.errors.authentication import AuthenticationError
from app.domain.errors.conflict import ConflictError


class AuthService:
    def __init__(
        self, users: UserRepository, hasher: PasswordHasher, tokens: TokenCodec, uow: UnitOfWork
    ) -> None:
        self._users = users
        self._hasher = hasher
        self._tokens = tokens
        self._uow = uow

    def register(self, command: RegisterUserCommand) -> User:
        return self._register(command, Role.CUSTOMER)

    def create_admin(self, command: RegisterUserCommand) -> User:
        return self._register(command, Role.ADMIN)

    def _register(self, command: RegisterUserCommand, role: Role) -> User:
        with self._uow.transaction():
            email = str(command.email).strip().lower()
            if self._users.by_email(email):
                raise ConflictError("email_exists", "This email is already registered.")
            user = User(command.name, email, self._hasher.hash(command.password), role)
            self._users.add(user)
        return user

    def login(self, email: str, password: str) -> AuthenticatedSession:
        user = self._users.by_email(email.strip().lower())
        valid = self._hasher.verify(password, user.password_hash if user else None)
        if not user or not valid:
            raise AuthenticationError("invalid_credentials", "Invalid email or password.")
        return AuthenticatedSession(user=user, access_token=self._tokens.issue(user.id))

    def current_user(self, token: str) -> User:
        user = self._users.by_id(self._tokens.decode(token))
        if user is None:
            raise AuthenticationError("invalid_token", "A valid access token is required.")
        return user
