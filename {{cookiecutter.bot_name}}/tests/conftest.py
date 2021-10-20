from dotenv import load_dotenv

load_dotenv(".env")


pytest_plugins = ["asyncbox.tests.fixtures"]
