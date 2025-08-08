import pytest

from app.decorators.mapper.exception_mapper import ExceptionMapper
from tests.unit.decorators.test_classes import (
    ChildError,
    DummyFactory,
    GeneratedError,
    ParentError,
    UnmappedError,
)


def test_sync_exception_mapping() -> None:
    """Test that the exception mapper works fine with sync functions."""

    def sync_function() -> None:
        raise ChildError("sync error")

    mapper = ExceptionMapper(
        {
            ParentError: DummyFactory("mapped"),
        }
    )

    wrapped = mapper(sync_function)

    with pytest.raises(GeneratedError) as exc_info:
        wrapped()

    assert str(exc_info.value).startswith("[mapped] sync error")
    assert isinstance(exc_info.value.__cause__, ChildError)


def test_sync_exception_mapping_works_fine_with_mutlticatch() -> None:
    """Test that the exception mapper works fine with sync functions."""

    def sync_function(error_type: type[Exception]) -> None:
        raise error_type("test_error")

    mapper = ExceptionMapper(
        {
            (ValueError, TypeError): DummyFactory("multicatch"),
            ZeroDivisionError: DummyFactory("singlecatch"),
        }
    )

    wrapped = mapper(sync_function)

    # 1. Check for first exception in multicatch
    with pytest.raises(GeneratedError) as exc_info:
        wrapped(ValueError)

    assert str(exc_info.value).startswith("[multicatch] test_error")

    # 2. Check for last exception in multicatch
    with pytest.raises(GeneratedError) as exc_info:
        wrapped(TypeError)

    assert str(exc_info.value).startswith("[multicatch] test_error")

    # 3. Check for single exception
    with pytest.raises(GeneratedError) as exc_info:
        wrapped(ZeroDivisionError)

    assert str(exc_info.value).startswith("[singlecatch] test_error")


@pytest.mark.asyncio
async def test_async_exception_mapping() -> None:
    """Test that the exception mapper works fine with async functions."""

    def async_function() -> None:
        raise ChildError("async error")

    mapper = ExceptionMapper(
        {
            ParentError: DummyFactory("mapped"),
        }
    )

    wrapped = mapper(async_function)

    with pytest.raises(GeneratedError) as exc_info:
        await wrapped()

    assert str(exc_info.value).startswith("[mapped] async error")
    assert isinstance(exc_info.value.__cause__, ChildError)


@pytest.mark.asyncio
async def test_catchall_mapping() -> None:
    """Test that the exception mapper works fine with Exception in mapping."""
    mapper = ExceptionMapper(
        {
            ChildError: DummyFactory("mapped"),
            Exception: DummyFactory("catchall"),
        }
    )

    def raise_unmapped() -> None:
        raise UnmappedError("unmapped!")

    wrapped = mapper(raise_unmapped)

    with pytest.raises(GeneratedError) as exc_info:
        await wrapped()

    assert str(exc_info.value) == "[catchall] unmapped!"
    assert isinstance(exc_info.value.__cause__, UnmappedError)


@pytest.mark.asyncio
async def test_no_mapping_no_catchall() -> None:
    """Test that the exception mapper works fine then non mapped exception is raised."""
    mapper = ExceptionMapper({})

    async def raise_unknown() -> None:
        raise UnmappedError("unmapped!")

    wrapped = mapper(raise_unknown)

    with pytest.raises(UnmappedError):
        await wrapped()


def test_sync_function_no_exception() -> None:
    """Test that the decorator passes through when no exception is raised."""

    mapper = ExceptionMapper(
        {
            ParentError: DummyFactory("mapped"),
        }
    )

    @mapper
    def test_func() -> str:
        return "success"

    assert test_func() == "success"


def test_mapper_works_fine_then_child_and_parent_in_map() -> None:
    mapper = ExceptionMapper(
        exception_map={
            ChildError: DummyFactory("child"),
            ParentError: DummyFactory("parent"),
            TypeError: DummyFactory("other"),
        },
        max_cache_size=1,
    )

    @mapper
    def function(exception: type[Exception]) -> None:
        raise exception("Error")

    # 1. DummyChild raised and put in cache
    with pytest.raises(GeneratedError) as exc_info:
        function(ChildError)

    assert str(exc_info.value).startswith("[child]")
    assert isinstance(exc_info.value.__cause__, ChildError)

    # 2. TypeError raised and put in cache
    with pytest.raises(GeneratedError) as exc_info:
        function(TypeError)

    assert isinstance(exc_info.value.__cause__, TypeError)
    assert str(exc_info.value).startswith("[other]")

    # 3. DummyException raised and put in cache
    with pytest.raises(GeneratedError) as exc_info:
        function(ParentError)
    assert isinstance(exc_info.value.__cause__, ParentError)
    assert str(exc_info.value).startswith("[parent]")


def test_nested_exception_mappers() -> None:
    """Test that nested exception mappers preserve the exception chain."""

    child_mapper = ExceptionMapper(
        exception_map={
            ChildError: DummyFactory("child"),
        }
    )

    parent_mapper = ExceptionMapper(
        exception_map={
            ParentError: DummyFactory("parent"),
        }
    )

    @parent_mapper
    @child_mapper
    def function(exception: type[Exception]) -> None:
        raise exception("Error")

    with pytest.raises(GeneratedError) as exc_info:
        function(ChildError)

    assert str(exc_info.value).startswith("[child]")
    assert isinstance(exc_info.value.__cause__, ChildError)

    with pytest.raises(GeneratedError) as exc_info:
        function(ParentError)

    assert str(exc_info.value).startswith("[parent]")
    assert isinstance(exc_info.value.__cause__, ParentError)


def test_sync_function_detailed_error_message() -> None:
    """Test that the decorator pass right context to the exception factory"""

    mapper = ExceptionMapper(
        exception_map={ChildError: DummyFactory("child", detailed=True)}
    )

    @mapper
    def test_func(arg1: str, arg2: str) -> None:
        raise ChildError("Original error")

    with pytest.raises(GeneratedError) as exc_info:
        test_func("value1", "value2")

    error_message = str(exc_info.value)
    assert "[child]" in error_message
    assert "test_func" in error_message
    assert "Args: [value1, value2]" in error_message
