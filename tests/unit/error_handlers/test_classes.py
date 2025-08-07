from pybotx import Bot, IncomingMessage

from app.presentation.bot.error_handlers.base_handlers import AbstractExceptionHandler


class TestExceptionHandler(AbstractExceptionHandler):
    def __init__(
        self,
        index: int,
        run_history: list,
        should_process_exception: bool = True,
        stop_on_failure: bool = False,
        break_the_chain: bool = False,
    ):
        self.index = index
        self.should_process_exception_flag = should_process_exception
        self.run_history = run_history

        super().__init__(None,stop_on_failure,break_the_chain)

    def should_process_exception(
        self, exc: Exception, bot: Bot, message: IncomingMessage
    ) -> bool:
        return self.should_process_exception_flag

    async def process_exception(self, *args, **kwargs):
        self.run_history.append(self.index)
