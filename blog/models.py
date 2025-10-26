"""Data models used by the Blog de Café utilities."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterable, List


@dataclass(frozen=True, slots=True)
class Post:
    """Represents a published blog post.

    Attributes
    ----------
    id:
        Unique identifier of the post.
    title:
        Human readable title of the article.
    slug:
        URL-friendly identifier used to reference the post.
    created_at:
        Datetime when the post was first published.
    tags:
        Optional list of topic tags describing the post.
    """

    id: int
    title: str
    slug: str
    created_at: datetime
    tags: List[str] = field(default_factory=list)

    def matches_query(self, query: str) -> bool:
        """Return True when the post matches the provided search query.

        The current implementation considers both the title and the tags, making
        it suitable for building simple autocomplete or quick search features.
        """

        normalized_query = query.strip().casefold()
        if not normalized_query:
            return True

        in_title = normalized_query in self.title.casefold()
        in_tags = any(normalized_query in tag.casefold() for tag in self.tags)
        return in_title or in_tags

    @staticmethod
    def from_dict(data: dict) -> "Post":
        """Build a :class:`Post` instance from a dictionary."""

        tags = data.get("tags", []) or []
        tags = list(tags) if isinstance(tags, Iterable) else [tags]
        return Post(
            id=int(data["id"]),
            title=str(data["title"]),
            slug=str(data["slug"]),
            created_at=_ensure_datetime(data["created_at"]),
            tags=[str(tag) for tag in tags],
        )


def _ensure_datetime(value: object) -> datetime:
    if isinstance(value, datetime):
        return value

    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError as exc:  # pragma: no cover - error path
            raise ValueError("Invalid datetime string") from exc

    raise TypeError("created_at value must be a datetime or ISO formatted string")
