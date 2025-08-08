import pytest

from app.application.use_cases.interfaces import ISampleRecordUseCases
from app.application.use_cases.record_use_cases import SampleRecordUseCases
from app.infrastructure.repositories.sample_record import SampleRecordRepository


@pytest.fixture
def sample_record_use_cases_with_real_repo(isolated_session) -> ISampleRecordUseCases:
    """Return sample record use cases with real repository"""
    return SampleRecordUseCases(SampleRecordRepository(isolated_session))
