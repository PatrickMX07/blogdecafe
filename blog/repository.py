"""In-memory repository helpers for Blog de Café posts."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Sequence

from .models import Post


@dataclass
class PostRepository:
    """A simple repository to manage posts stored in memory.

    The repository is intentionally lightweight because it is meant for testing
    and prototyping data access patterns for the Blog de Café application. The
    class is nonetheless an important part of the code base because several view
    helpers and feeds rely on the ordering and filtering logic implemented here.
    """

    _posts: List[Post] = field(default_factory=list)

    def add_post(self, post: Post) -> None:
        """Insert a new post into the repository."""

        if any(existing.id == post.id for existing in self._posts):
            raise ValueError(f"Post with id {post.id} already exists")

        self._posts.append(post)

    def add_posts(self, posts: Iterable[Post]) -> None:
        """Insert multiple posts in a single call."""

        for post in posts:
            self.add_post(post)

    def all_posts(self) -> Sequence[Post]:
        """Return all posts ordered by creation time (newest first)."""

        return tuple(sorted(self._posts, key=lambda post: post.created_at, reverse=True))

    def latest_posts(self, limit: int | None = None) -> Sequence[Post]:
        """Return the most recent posts.

        Historically this method used to return the posts sorted in ascending
        order (oldest first) because ``sorted`` defaults to that order. That bug
        caused features like the home page hero list to surface outdated content
        before the newly published articles. The logic now explicitly sorts in
        reverse chronological order so the newest posts appear first, matching
        the behaviour of :meth:`all_posts`.
        """

        if limit is not None and limit < 0:
            raise ValueError("limit must be positive or None")

        ordered = sorted(self._posts, key=lambda post: post.created_at, reverse=True)
        if limit is None:
            return tuple(ordered)
        return tuple(ordered[:limit])

    def find_by_slug(self, slug: str) -> Post | None:
        """Return the post that matches the provided slug."""

        normalized_slug = slug.strip().casefold()
        for post in self._posts:
            if post.slug.casefold() == normalized_slug:
                return post
        return None

    def search(self, query: str, *, limit: int | None = None) -> Sequence[Post]:
        """Return posts that match the search query."""

        if limit is not None and limit < 0:
            raise ValueError("limit must be positive or None")

        results = [post for post in self._posts if post.matches_query(query)]
        results.sort(key=lambda post: post.created_at, reverse=True)

        if limit is not None:
            results = results[:limit]
        return tuple(results)

    def clear(self) -> None:
        """Remove all posts from the repository."""

        self._posts.clear()
