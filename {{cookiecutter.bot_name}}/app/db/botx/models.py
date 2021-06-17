"""BotX models for users and chats."""
from botx import ChatTypes
from tortoise import fields, models

HOST_MAX_LENGTH = 255
CHAT_TYPE_MAX_LENGTH = 16


class BotXCTS(models.Model):
    """Model for cts. Has host only."""

    host = fields.CharField(pk=True, max_length=HOST_MAX_LENGTH)

    bots: fields.ReverseRelation["BotXBot"]
    chats: fields.ReverseRelation["BotXChat"]

    def __str__(self) -> str:  # noqa: D105
        return f"<{self.__class__.__name__} host: {self.host}>"


class BotXBot(models.Model):
    """Model for bot. Bot is chat member like user, but has less fields."""

    bot_id = fields.UUIDField(pk=True)
    name = fields.TextField(null=True)
    # allow to find current bot in chats
    current_bot = fields.BooleanField(default=False)
    cts: fields.ForeignKeyRelation[BotXCTS] = fields.ForeignKeyField(
        "botx.BotXCTS", related_name="bots", on_delete=fields.CASCADE
    )

    def __str__(self) -> str:  # noqa: D105
        model = self.__class__.__name__
        return "<{0} bot_id: {1} current: {2}>".format(
            model, self.bot_id, self.current_bot
        )


class BotXUser(models.Model):
    """Model for chat member. If user on the same cts with bot botx send all fields."""

    user_huid = fields.UUIDField(pk=True)
    username = fields.TextField(null=True)
    ad_login = fields.TextField(null=True)
    ad_domain = fields.TextField(null=True)
    cts: fields.ForeignKeyRelation[BotXCTS] = fields.ForeignKeyField(
        "botx.BotXCTS", related_name="users", on_delete=fields.CASCADE
    )

    chats: fields.ManyToManyRelation["BotXChat"]
    created_chats: fields.ReverseRelation["BotXChat"]
    administered_chats: fields.ManyToManyRelation["BotXChat"]

    class Meta:
        unique_together = (("ad_login", "ad_domain"),)

    def __str__(self) -> str:  # noqa: D105
        return f"<{self.__class__.__name__} user_huid: {self.user_huid}>"


class BotXChat(models.Model):
    """Model for chat. Has members and meta info like chat type, last sync_id, etc."""

    group_chat_id = fields.UUIDField(pk=True)
    chat_type = fields.CharEnumField(ChatTypes, max_length=CHAT_TYPE_MAX_LENGTH)

    last_sync_id = fields.UUIDField(null=True)

    creator: fields.ForeignKeyRelation[BotXUser] = fields.ForeignKeyField(
        "botx.BotXUser",
        related_name="created_chats",
        null=True,
        on_delete=fields.SET_NULL,
    )

    cts: fields.ForeignKeyRelation[BotXCTS] = fields.ForeignKeyField(
        "botx.BotXCTS", related_name="chats", on_delete=fields.CASCADE
    )
    admins: fields.ManyToManyRelation[BotXUser] = fields.ManyToManyField(
        "botx.BotXUser", related_name="administered_chats", through="chat_user_admins"
    )
    members: fields.ManyToManyRelation[BotXUser] = fields.ManyToManyField(
        "botx.BotXUser", related_name="chats", through="chat_user_members"
    )

    def __str__(self) -> str:  # noqa: D105
        return "<{0} group_chat_id: {1} chat_type: {2}>".format(
            self.__class__.__name__, self.group_chat_id, self.chat_type
        )
