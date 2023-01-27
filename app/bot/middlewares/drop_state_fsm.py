"""Middleware to drop state of FSM in case of using pybotx-fsm."""
from pybotx import Bot, IncomingMessage, IncomingMessageHandlerFunc


async def drop_state_middleware(
    message: IncomingMessage, bot: Bot, call_next: IncomingMessageHandlerFunc
) -> None:
    try:
        await call_next(message, bot)
    except Exception as message_handler_exc:
        fsm_manager = getattr(message.state, "fsm", None)
        if fsm_manager:
            await fsm_manager.drop_state()

        raise message_handler_exc
