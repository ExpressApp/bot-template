import uuid

import asyncpg.pgproto.pgproto
from pydantic import BaseModel


class ModelWithUUID(BaseModel):
    my_id: uuid.UUID


def test_uuid_monkey_patch_applies() -> None:
    uuid_value = uuid.uuid4()
    asyncpg_value = asyncpg.pgproto.pgproto.UUID(str(uuid_value))

    model = ModelWithUUID(my_id=asyncpg_value)
    assert model.my_id == uuid_value
