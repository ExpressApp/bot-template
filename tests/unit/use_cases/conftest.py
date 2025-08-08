import pytest

from app.application.use_cases.interfaces import ISampleRecordUseCases
from app.application.use_cases.record_use_cases import SampleRecordUseCases
from tests.unit.use_cases.fake_repository import FakeSampleRecordRepository


@pytest.fixture
def sample_record_use_cases_with_fake_repo() -> ISampleRecordUseCases:
    """Return sample record use cases with fake repository"""
    return SampleRecordUseCases(FakeSampleRecordRepository())
