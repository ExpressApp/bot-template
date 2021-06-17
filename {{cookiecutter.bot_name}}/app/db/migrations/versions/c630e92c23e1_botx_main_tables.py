"""botx main tables

Revision ID: c630e92c23e1
Revises: 
Create Date: 2019-06-28 17:22:48.360104

Doc: https://alembic.sqlalchemy.org/en/latest/tutorial.html#create-a-migration-script
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision = "c630e92c23e1"
down_revision = None
branch_labels = None
depends_on = None


def create_botxcts_table():
    op.create_table("botxcts", sa.Column("host", sa.Text, primary_key=True))


def create_botxbot_table():
    op.create_table(
        "botxbot",
        sa.Column("bot_id", UUID, primary_key=True),
        sa.Column("name", sa.Text),
        sa.Column("current_bot", sa.Boolean, default=False),
        sa.Column(
            "cts_id",
            sa.Text,
            sa.ForeignKey("botxcts.host", ondelete="CASCADE"),
            nullable=False,
        ),
    )
    op.execute(
        """
        CREATE OR REPLACE FUNCTION check_only_one_current_bot_on_cts()
            RETURNS TRIGGER AS
        $$
        BEGIN
            IF NEW.current_bot = TRUE AND (TG_OP = 'INSERT' OR TG_OP = 'UPDATE') THEN
                IF NEW.cts_id IN (
                    SELECT cts_id
                    FROM "botxbot"
                    WHERE current_bot = TRUE AND bot_id != NEW.bot_id
                    GROUP BY cts_id
                ) THEN
                    RAISE EXCEPTION '% cts already has registered main bot', NEW.cts_id;
                END IF;
            END IF;

            RETURN NEW;
        END;
        $$ LANGUAGE 'plpgsql';

        CREATE TRIGGER check_only_one_current_bot_on_cts_trigger
            BEFORE INSERT OR UPDATE
            ON "botxbot"
            FOR EACH ROW
        EXECUTE PROCEDURE check_only_one_current_bot_on_cts();
        """
    )


def create_botxuser_table():
    op.create_table(
        "botxuser",
        sa.Column("user_huid", UUID, primary_key=True),
        sa.Column("username", sa.Text),
        sa.Column("ad_login", sa.Text),
        sa.Column("ad_domain", sa.Text),
        sa.Column("cts_id", sa.Text, sa.ForeignKey("botxcts.host", ondelete="CASCADE")),
    )


def create_botxchat_table():
    op.create_table(
        "botxchat",
        sa.Column("group_chat_id", UUID, primary_key=True),
        sa.Column("last_sync_id", UUID),
        sa.Column("chat_type", sa.Text, nullable=False),
        sa.Column(
            "creator_id", UUID, sa.ForeignKey("botxuser.user_huid", ondelete="SET NULL")
        ),
        sa.Column(
            "cts_id",
            sa.Text,
            sa.ForeignKey("botxcts.host", ondelete="CASCADE"),
            nullable=False,
        ),
    )


def create_chat_admins_table():
    op.create_table(
        "chat_user_admins",
        sa.Column(
            "botxchat_id",
            UUID,
            sa.ForeignKey("botxchat.group_chat_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "botxuser_id",
            UUID,
            sa.ForeignKey("botxuser.user_huid", ondelete="CASCADE"),
            nullable=False,
        ),
    )
    op.create_primary_key(
        "pk_chat_user_admins", "chat_user_admins", ["botxchat_id", "botxuser_id"]
    )


def create_chat_members_table():
    op.create_table(
        "chat_user_members",
        sa.Column(
            "botxchat_id",
            UUID,
            sa.ForeignKey("botxchat.group_chat_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "botxuser_id",
            UUID,
            sa.ForeignKey("botxuser.user_huid", ondelete="CASCADE"),
            nullable=False,
        ),
    )
    op.create_primary_key(
        "pk_chat_user_members", "chat_user_members", ["botxchat_id", "botxuser_id"]
    )


def upgrade() -> None:
    create_botxcts_table()
    create_botxbot_table()
    create_botxuser_table()
    create_botxchat_table()
    create_chat_members_table()
    create_chat_admins_table()


def downgrade() -> None:
    op.drop_table("chat_user_members")
    op.drop_table("chat_user_admins")
    op.drop_table("botxchat")
    op.drop_table("botxuser")
    op.drop_table("botxbot")
    op.drop_table("botxcts")
