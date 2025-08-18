# tests/unit/test_schemas.py
# Author: Miguel Gonzalez Almonte
# Created: 2025-08-17
# Description: Unit test for dataframe schemas. Ensures tabular representations remain consistent over time.
# Role: Infrastructure/UI/Tests/Config



from datetime import date, datetime, timezone
from uuid import uuid4
import pandas as pd
import pytest

from core.types.dtos import SessionDTO, ItemDTO, LanguageDTO
from core.types.enums import Difficulty, ItemType, SessionStatus
from core.dataframes.schemas import (
    append_session,
    append_item,
    append_language,
    append_sessions_from_iterable,
    empty_sessions_df,
    empty_items_df,
    empty_languages_df,
    coerce_sessions_df,
    coerce_items_df,
    coerce_languages_df,
)

def test_empty_sessions_df():
    df = empty_sessions_df()
    assert len(df) == 0
    assert "session_id" in df.columns
    assert "hour_spent" in df.columns
    assert df["hour_spent"].dtype == "Float64"

def test_append_session():
    df = empty_sessions_df()
    session = SessionDTO(
        item_id=uuid4(),
        language_code="py",
        session_date=date.today(),
        hour_spent=1.5,
        difficulty=Difficulty.beginner,
        status=SessionStatus.completed,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        started_at=datetime.now(timezone.utc),
        ended_at=datetime.now(timezone.utc)
    )
    df = append_session(df, session)
    assert len(df) == 1
    assert df["hour_spent"].iloc[0] == 1.5
    assert df["difficulty"].iloc[0] == "beginner"

def test_append_item():
    df = empty_items_df()
    item = ItemDTO(
        item_type=ItemType.project,
        title="Test Project",
        language_code="py",
        description="A test project",
    )
    df = append_item(df, item)
    assert len(df) == 1
    assert df["title"].iloc[0] == "Test Project"
    assert df["item_type"].iloc[0] == "project"


def test_append_language():
    df = empty_languages_df()
    language = LanguageDTO(
        code="py",
        name="Python",
        slug="python",
        direction="ltr"
    )
    df = append_language(df, language)
    assert len(df) == 1
    assert df["code"].iloc[0] == "py"
    assert df["name"].iloc[0] == "Python"


def test_empty_items_df():
    df = empty_items_df()
    assert len(df) == 0
    assert "item_id" in df.columns
    assert "title" in df.columns
    assert df["title"].dtype == "string"


def test_empty_languages_df():
    df = empty_languages_df()
    assert len(df) == 0
    assert "id" in df.columns
    assert "code" in df.columns
    assert df["code"].dtype == "string"


def test_append_sessions_from_iterable():
    df = empty_sessions_df()
    sessions = [
        SessionDTO(
            item_id=uuid4(),
            language_code="py",
            session_date=date.today(),
            hour_spent=1.0,
            difficulty=Difficulty.beginner,
            status=SessionStatus.completed,
        ),
        SessionDTO(
            item_id=uuid4(),
            language_code="js",
            session_date=date.today(),
            hour_spent=2.0,
            difficulty=Difficulty.advanced,
            status=SessionStatus.in_progress,
        )
    ]
    df = append_sessions_from_iterable(df, sessions)
    assert len(df) == 2
    assert df["hour_spent"].iloc[0] == 1.0
    assert df["hour_spent"].iloc[1] == 2.0


def test_coerce_sessions_df():
    # Test with a malformed dataframe
    df = pd.DataFrame({
        "session_id": ["test-id"],
        "item_id": ["item-id"],
        "language_code": ["py"],
        "session_date": ["2024-01-01"],
        "hour_spent": [1.5],
        "difficulty": ["beginner"],
        "status": ["completed"],
        "topic": [None],
        "tags": [""],
        "notes": [None],
        "points_awarded": [10.0],
        "progress_pct": [100.0],
        "session_number": [1],
        "started_at": [None],
        "ended_at": [None],
        "created_at": [datetime.now(timezone.utc)],
        "updated_at": [datetime.now(timezone.utc)],
        "version": [1]
    })
    df_coerced = coerce_sessions_df(df)
    assert df_coerced["hour_spent"].dtype == "Float64"
    assert df_coerced["session_number"].dtype == "Int64"


def test_coerce_items_df():
    df = pd.DataFrame({
        "item_id": ["test-id"],
        "item_type": ["project"],
        "title": ["Test"],
        "language_code": ["py"],
        "description": [None],
        "created_at": [datetime.now(timezone.utc)],
        "updated_at": [datetime.now(timezone.utc)],
        "version": [1]
    })
    df_coerced = coerce_items_df(df)
    assert df_coerced["title"].dtype == "string"
    assert df_coerced["version"].dtype == "Int64"


def test_coerce_languages_df():
    df = pd.DataFrame({
        "id": ["test-id"],
        "code": ["py"],
        "name": ["Python"],
        "slug": ["python"],
        "direction": ["ltr"],
        "created_at": [datetime.now(timezone.utc)],
        "updated_at": [datetime.now(timezone.utc)]
    })
    df_coerced = coerce_languages_df(df)
    assert df_coerced["code"].dtype == "string"
    assert df_coerced["name"].dtype == "string"
