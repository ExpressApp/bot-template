from pydantic import BaseModel


class BotCommand(BaseModel):
    command_name: str
    description: str | None
    visible: bool = True

    def command_data(self) -> dict:
        return {
            "command_name": self.command_name,
            "description": self.description,
            "visible": self.visible,
        }


class SampleRecordCommands:
    CREATE_RECORD = BotCommand(
        command_name="/create_record",
        description="Создать запись",
    )

