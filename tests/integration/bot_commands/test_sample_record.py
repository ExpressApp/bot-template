from pybotx import Bot
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.sample_record.models import SampleRecordModel
from tests.integration.bot_commands.sample_record_factories import (
    CreateSampleRecordRequestFactory,
)


async def test_sample_record_created(
    bot: Bot,
    create_sample_record_command_message_factory,
    isolated_session: AsyncSession,
):
    """Test creating a record usual way."""
    request_data = CreateSampleRecordRequestFactory.create()
    message = create_sample_record_command_message_factory(request_data.json())
    await bot.async_execute_bot_command(message)

    # Check db object existing
    db_object: SampleRecordModel = await isolated_session.scalar(  # type: ignore
        select(SampleRecordModel).where(SampleRecordModel.name == request_data["name"])
    )

    assert db_object.record_data == request_data["record_data"]
    assert db_object.name == request_data["name"]

    # Check bot answer
    assert bot.answer_message.call_args[0][0] == (  # type: ignore
        f"Запись успешно создана:\n**id**: {db_object.id} "
        f"**name**: {db_object.name} "
        f"**record_data**: {db_object.record_data}."
    )


async def test_sample_record_delete(
    bot: Bot,
    isolated_session: AsyncSession,
    sample_record_factory,
    delete_sample_record_command_message_factory,
):
    """Test creating a record usual way."""
    existing_record: SampleRecordModel = await sample_record_factory.create()

    message = delete_sample_record_command_message_factory(existing_record.id)
    await bot.async_execute_bot_command(message)

    # Check db object non existing
    db_object: SampleRecordModel = await isolated_session.scalar(  # type: ignore
        select(SampleRecordModel).where(SampleRecordModel.id == existing_record.id)
    )

    assert db_object is None


async def test_get_sample_record(
    bot: Bot,
    sample_record_factory,
    get_sample_record_command_message_factory,
    isolated_session: AsyncSession,
):
    """Test get sample record."""
    existing_record: SampleRecordModel = await sample_record_factory.create()

    message = get_sample_record_command_message_factory(
        existing_record.id,
    )

    await bot.async_execute_bot_command(message)

    # Check bot answer
    assert bot.answer_message.call_args[0][0] == (  # type:ignore
        "Запись найдена:\n"
        f"**id**: {existing_record.id} "
        f"**name**: {existing_record.name} "
        f"**record_data**: {existing_record.record_data}."
    )
