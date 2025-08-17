from enum import Enum


class Difficulty(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"
    expert = "expert"


class ItemType(str, Enum):
    exercise = "exercise"
    project = "project"


class SessionStatus(str, Enum):
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


class PublishStatus(str, Enum):
    draft = "draft"
    published = "published"
    archived = "archived"


class Theme(str, Enum):
    light = "light"
    dark = "dark"
    system = "system"
