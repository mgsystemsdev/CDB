import pytest
from src.core.types.enums import Difficulty, ItemType, SessionStatus, PublishStatus, Theme

def test_difficulty_has_four_levels():
    assert {d.value for d in Difficulty} == {"beginner", "intermediate", "advanced", "expert"}

def test_item_type_values():
    assert [ItemType.exercise.value, ItemType.project.value] == ["exercise", "project"]

def test_session_status_values():
    assert {s.value for s in SessionStatus} == {"in_progress", "completed", "cancelled"}

def test_publish_status_values():
    assert {p.value for p in PublishStatus} == {"draft", "published", "archived"}

def test_theme_values_are_strings():
    for t in Theme:
        assert isinstance(t.value, str)
