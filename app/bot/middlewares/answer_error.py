"""Middleware to handle AnswerError and AnswerMessageError exceptions."""

from pybotx import Bot, IncomingMessage, IncomingMessageHandlerFunc

from app.services.answer_error import AnswerError, AnswerMessageError


async def answer_error_middleware(
    message: IncomingMessage, bot: Bot, call_next: IncomingMessageHandlerFunc
) -> None:
    try:
        await call_next(message, bot)
    except AnswerError as exc:
        await bot.send(
            message=exc.message,
            wait_callback=exc.wait_callback,
            callback_timeout=exc.callback_timeout,
        )
    except AnswerMessageError as exc:
        await bot.answer_message(
            body=exc.body,
            metadata=exc.metadata,
            bubbles=exc.bubbles,
            keyboard=exc.keyboard,
            file=exc.file,
            recipients=exc.recipients,
            silent_response=exc.silent_response,
            markup_auto_adjust=exc.markup_auto_adjust,
            stealth_mode=exc.stealth_mode,
            send_push=exc.send_push,
            ignore_mute=exc.ignore_mute,
            wait_callback=exc.wait_callback,
            callback_timeout=exc.callback_timeout,
        )
