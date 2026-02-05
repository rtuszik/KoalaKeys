import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def fixtures_dir():
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def valid_fixtures(fixtures_dir):
    return fixtures_dir / "valid"


@pytest.fixture
def invalid_fixtures(fixtures_dir):
    return fixtures_dir / "invalid"


@pytest.fixture
def valid_yaml_data():
    return {
        "title": "Test Cheatsheet",
        "layout": {"keyboard": "US", "system": "Darwin"},
        "shortcuts": {"General": {"CMD+C": {"description": "Copy"}}},
    }


@pytest.fixture
def sample_system_mappings():
    return {"cmd": "⌘", "ctrl": "⌃", "alt": "⌥", "shift": "⇧"}


@pytest.fixture
def sample_keyboard_layouts():
    return {"US": {"layout": [["Esc", "F1", "F2"], ["`", "1", "2", "3"], ["Tab", "Q", "W", "E"]]}}
