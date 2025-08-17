from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Dict, Iterable
from uuid import UUID

import numpy as np
import pandas as pd
from pandas import DatetimeTZDtype

from src.core.types.dtos import ItemDTO, LanguageDTO, SessionDTO

# ---------- Canonical schemas (column -> dtype) ----------

UTC = DatetimeTZDtype("ns", "UTC")

SESSIONS_SCHEMA: Dict[str, object] = {
    "session_id": "string",
    "item_id": "string",
    "language_code": "string",
    "session_date": "string",  # store ISO date (YYYY-MM-DD) as string; keep simple
    "hour_spent": "Float64",
    "difficulty": "string",
    "status": "string",
    "topic": "string",
    "tags": "string",  # JSON-ish serialized list; simple start
    "notes": "string",
    "points_awarded": "Float64",
    "progress_pct": "Float64",
    "session_number": "Int64",
    "started_at": UTC,
    "ended_at": UTC,
    "created_at": UTC,
    "updated_at": UTC,
    "version": "Int64",
}

ITEMS_SCHEMA: Dict[str, object] = {
    "item_id": "string",
    "item_type": "string",
    "title": "string",
    "language_code": "string",
    "description": "string",
    "created_at": UTC,
    "updated_at": UTC,
    "version": "Int64",
}

LANGUAGES_SCHEMA: Dict[str, object] = {
    "id": "string",
    "code": "string",
    "name": "string",
    "slug": "string",
    "direction": "string",
    "created_at": UTC,
    "updated_at": UTC,
}

# ---------- Factory helpers ----------


def _empty_df(schema: Dict[str, object]) -> pd.DataFrame:
    df = pd.DataFrame(
        {col: pd.Series(dtype=str(dtype)) for col, dtype in schema.items()}
    )
    # Ensure timezone dtypes are applied even when empty
    for col, dtype in schema.items():
        if isinstance(dtype, DatetimeTZDtype):
            df[col] = pd.Series([], dtype=dtype)
    return df


def empty_sessions_df() -> pd.DataFrame:
    return _empty_df(SESSIONS_SCHEMA)


def empty_items_df() -> pd.DataFrame:
    return _empty_df(ITEMS_SCHEMA)


def empty_languages_df() -> pd.DataFrame:
    return _empty_df(LANGUAGES_SCHEMA)


# ---------- Coercion helpers ----------

from typing import Any


def _to_utc_dt(value: Any) -> pd.Timestamp | type(pd.NaT):
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return pd.NaT
    if isinstance(value, pd.Timestamp):
        return value.tz_convert("UTC") if value.tzinfo else value.tz_localize("UTC")
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return pd.Timestamp(value).tz_convert("UTC")
    # strings
    ts = pd.to_datetime(value, errors="coerce", utc=True)


def _coerce_df(
    df: pd.DataFrame, schema: Dict[str, object], allow_extra: bool = False
) -> pd.DataFrame:
    # Add missing cols
    for col, dtype in schema.items():
        if col not in df.columns:
            df[col] = pd.Series(
                [pd.NA] * len(df),
                dtype=dtype if not isinstance(dtype, DatetimeTZDtype) else dtype,
            )

    # Drop extras if not allowed
    if not allow_extra:
        df = df[[*schema.keys()]]

    # Coerce types
    for col, dtype in schema.items():
        if isinstance(dtype, DatetimeTZDtype):
            # Handle timezone conversion properly
            df[col] = pd.to_datetime(df[col], errors="coerce", utc=True)
            if df[col].dt.tz is None:
                df[col] = df[col].dt.tz_localize("UTC")
            else:
                df[col] = df[col].dt.tz_convert("UTC")
        else:
            # Special-case string columns: ensure pandas string dtype
            if dtype == "string":
                df[col] = df[col].astype("string")
            else:
                # Int64/Float64 nullable handling
                try:
                    df[col] = df[col].astype(dtype)
                except TypeError:
                    # Some mixed objects → try to_numeric where applicable
                    if dtype in ("Int64", "Float64"):
                        df[col] = pd.to_numeric(df[col], errors="coerce").astype(dtype)
                    else:
                        df[col] = df[col].astype("string").astype(dtype)
    return df


def coerce_sessions_df(df: pd.DataFrame, allow_extra: bool = False) -> pd.DataFrame:
    return _coerce_df(df.copy(), SESSIONS_SCHEMA, allow_extra=allow_extra)


def coerce_items_df(df: pd.DataFrame, allow_extra: bool = False) -> pd.DataFrame:
    return _coerce_df(df.copy(), ITEMS_SCHEMA, allow_extra=allow_extra)


def coerce_languages_df(df: pd.DataFrame, allow_extra: bool = False) -> pd.DataFrame:
    return _coerce_df(df.copy(), LANGUAGES_SCHEMA, allow_extra=allow_extra)


# ---------- Append helpers from DTOs ----------


def _iso_date(d: date | None) -> str | None:
    return d.isoformat() if d else None


def append_session(df: pd.DataFrame, dto: SessionDTO) -> pd.DataFrame:
    if df.empty:
        df = empty_sessions_df()
    row = {
        "session_id": str(dto.session_id),
        "item_id": str(dto.item_id),
        "language_code": dto.language_code,
        "session_date": _iso_date(dto.session_date),
        "hour_spent": dto.hours_spent,
        "difficulty": dto.difficulty.value,
        "status": dto.status.value,
        "topic": dto.topic,
        "tags": ",".join(dto.tags) if dto.tags else None,
        "notes": dto.notes,
        "points_awarded": dto.points_awarded,
        "progress_pct": dto.progress_pct,
        "session_number": dto.session_number,
        "started_at": dto.started_at,
        "ended_at": dto.ended_at,
        "created_at": dto.created_at,
        "updated_at": dto.updated_at,
        "version": dto.version,
    }
    new_row_df = pd.DataFrame([row])
    if df.empty:
        df = new_row_df
    else:
        df = pd.concat([df, new_row_df], ignore_index=True)
    return coerce_sessions_df(df)


def append_item(df: pd.DataFrame, dto: ItemDTO) -> pd.DataFrame:
    if df.empty:
        df = empty_items_df()
    row = {
        "item_id": str(dto.item_id),
        "item_type": dto.item_type.value,
        "title": dto.title,
        "language_code": dto.language_code,
        "description": dto.description,
        "created_at": dto.created_at,
        "updated_at": dto.updated_at,
        "version": dto.version,
    }
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    return coerce_items_df(df)


def append_language(df: pd.DataFrame, dto: LanguageDTO) -> pd.DataFrame:
    if df.empty:
        df = empty_languages_df()
    row = {
        "id": str(dto.id),
        "code": dto.code,
        "name": dto.name,
        "slug": dto.slug,
        "direction": dto.direction,
        "created_at": dto.created_at,
        "updated_at": dto.updated_at,
    }
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    return coerce_languages_df(df)


def append_sessions_from_iterable(
    df: pd.DataFrame, sessions: Iterable[SessionDTO]
) -> pd.DataFrame:
    for session in sessions:
        df = append_session(df, session)
    return df
