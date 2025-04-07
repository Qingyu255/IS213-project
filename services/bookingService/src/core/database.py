from typing import Generator

def get_db() -> Generator:
    """
    Dummy database dependency that yields None since this service doesn't need direct database access.
    It orchestrates other services that handle their own data storage.
    """
    yield None 