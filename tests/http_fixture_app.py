"""Socket smoke-test app only. Never use this module for deployment or judging."""

from config import Settings
from main import create_app
from test_api import FixtureInterpreter

app = create_app(Settings(), FixtureInterpreter())
