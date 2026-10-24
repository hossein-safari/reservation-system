from collections.abc import Iterator
from contextlib import contextmanager

from app.application.service_scope import ServiceScope
from app.application.services.auth import AuthService
from app.application.services.payments import PaymentService
from app.application.services.reservations import ReservationService
from app.application.services.resources import ResourceService
from app.application.services.slots import SlotService
from app.application.services.transactions import TransactionService
from app.config import Settings
from app.infrastructure.clock import SystemClock
from app.infrastructure.payments.development_gateway import DevelopmentGateway
from app.infrastructure.persistence.database import Database
from app.infrastructure.persistence.models import configure_mappings
from app.infrastructure.persistence.repositories.payment import SqlPaymentRepository
from app.infrastructure.persistence.repositories.reservation import SqlReservationRepository
from app.infrastructure.persistence.repositories.resource import SqlResourceRepository
from app.infrastructure.persistence.repositories.slot import SqlSlotRepository
from app.infrastructure.persistence.repositories.transaction import SqlTransactionRepository
from app.infrastructure.persistence.repositories.user import SqlUserRepository
from app.infrastructure.persistence.unit_of_work import SqlUnitOfWork
from app.infrastructure.security.password_hasher import ArgonPasswordHasher
from app.infrastructure.security.token_codec import JwtTokenCodec


class ApplicationContainer:
    """Composition root: the sole place that selects concrete adapters."""

    def __init__(self, settings: Settings) -> None:
        configure_mappings()
        self.database = Database(settings.database_url)
        self.clock = SystemClock()
        self.hasher = ArgonPasswordHasher()
        self.tokens = JwtTokenCodec(
            settings.app_secret_key, settings.access_token_minutes, self.clock
        )
        self.gateway = DevelopmentGateway(settings.app_env)

    @contextmanager
    def scope(self) -> Iterator[ServiceScope]:
        with self.database.session() as session:
            users = SqlUserRepository(session)
            resources = SqlResourceRepository(session)
            slots = SqlSlotRepository(session, self.clock)
            bookings = SqlReservationRepository(session)
            payments = SqlPaymentRepository(session)
            transactions = SqlTransactionRepository(session)
            uow = SqlUnitOfWork(session)
            yield ServiceScope(
                auth=AuthService(users, self.hasher, self.tokens, uow),
                resources=ResourceService(resources, uow),
                slots=SlotService(resources, slots, uow, self.clock),
                reservations=ReservationService(bookings, slots, uow, self.clock),
                payments=PaymentService(
                    bookings, payments, transactions, self.gateway, uow, self.clock
                ),
                transactions=TransactionService(transactions),
            )

    def close(self) -> None:
        self.database.close()
