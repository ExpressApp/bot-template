from app.decorators.exception_mapper import ExceptionContext, ExceptionFactory


class ParentError(Exception):
    """Parent error class."""


class ChildError(ParentError):
    """Child error class."""


class UnmappedError(Exception):
    """Unmapped error class."""


class GeneratedError(Exception):
    """Generated error class."""


class DummyFactory(ExceptionFactory):
    """Dummy factory class."""

    def __init__(
        self,
        tag: str,
        generated_exception: type[Exception] = GeneratedError,
        detailed: bool = False,
    ) -> None:
        self.tag = tag
        self.generated_exception = generated_exception
        self.detailed = detailed

    def make_exception(self, context: ExceptionContext) -> Exception:
        if self.detailed:
            return self.generated_exception(
                f"[{self.tag}] {str(context.formatted_context)}"
            )

        return self.generated_exception(
            f"[{self.tag}] {str(context.original_exception)}"
        )
