"""Dependencies for get status recipient."""
from typing import Optional
from uuid import UUID

from botx import ChatTypes
from botx.models.status import StatusRecipient


async def get_status_recipient(
    bot_id: UUID,
    user_huid: UUID,
    chat_type: ChatTypes,
    ad_login: Optional[str] = None,
    ad_domain: Optional[str] = None,
    is_admin: Optional[str] = None,  # Hack with casting "" to bool.
) -> StatusRecipient:
    """Get status recipient from status request query params."""

    if is_admin is not None:
        is_admin_bool = is_admin.lower() == "true"
    else:
        is_admin_bool = False

    return StatusRecipient(
        bot_id=bot_id,
        user_huid=user_huid,
        ad_login=ad_login,
        ad_domain=ad_domain,
        is_admin=is_admin_bool,
        chat_type=chat_type,
    )
