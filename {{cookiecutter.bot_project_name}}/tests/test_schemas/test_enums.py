from app.schemas.enums import StrEnum


def test_str_enum():
    class MyStrEnum(StrEnum):
        test_field = "test"

    assert isinstance(MyStrEnum.test_field, str)
