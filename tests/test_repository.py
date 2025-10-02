from datetime import datetime, timedelta

import pytest

from blog import Post, PostRepository


def make_post(idx: int, *, hours_ago: int) -> Post:
    created_at = datetime.now() - timedelta(hours=hours_ago)
    return Post(
        id=idx,
        title=f"Post {idx}",
        slug=f"post-{idx}",
        created_at=created_at,
        tags=["cafe", "receta" if idx % 2 == 0 else "grano"],
    )


def test_latest_posts_returns_most_recent_first():
    repo = PostRepository()
    posts = [make_post(idx, hours_ago=(5 - idx) * 2) for idx in range(1, 5)]

    repo.add_posts(posts)

    latest = repo.latest_posts()
    assert [post.id for post in latest] == [4, 3, 2, 1]

    limited = repo.latest_posts(limit=2)
    assert [post.id for post in limited] == [4, 3]


def test_latest_posts_rejects_negative_limit():
    repo = PostRepository()

    with pytest.raises(ValueError):
        repo.latest_posts(limit=-1)


def test_search_keeps_newest_first_and_respects_limit():
    repo = PostRepository()
    repo.add_posts(
        [
            make_post(1, hours_ago=10),
            make_post(2, hours_ago=5),
            make_post(3, hours_ago=1),
        ]
    )

    results = repo.search("post")
    assert [post.id for post in results] == [3, 2, 1]

    results_limited = repo.search("post", limit=2)
    assert [post.id for post in results_limited] == [3, 2]
