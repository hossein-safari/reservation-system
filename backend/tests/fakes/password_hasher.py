class FakePasswordHasher:
    def __init__(self) -> None:
        self.verified_hashes: list[str | None] = []

    def hash(self, password: str) -> str:
        return f"test-only-{password}"

    def verify(self, password: str, hashed: str | None) -> bool:
        self.verified_hashes.append(hashed)
        return hashed == self.hash(password)
