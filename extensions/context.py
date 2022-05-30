import os

from copier_templates_extensions import ContextHook
from copier.errors import UserMessageError


class ContextUpdater(ContextHook):
    def hook(self, context):
        try:
            context["PROD_SERVER_HOST"] = os.environ["PROD_SERVER_HOST"]
            context["DEV_SERVER_HOST"] = os.environ["DEV_SERVER_HOST"]
        except KeyError as exc:
            raise UserMessageError(f"{exc.args[0]} is not provided in environment")
        context["registry_url"] = os.getenv("BOTS_REGISTRY_URL") or context["registry_url"]
        return context
