from abc import ABC
import json


class Subject:
    def __init__(self, id=None):
        self.id: int = id
        self.name: str
        self.type: str
        self.date: str

        self.aliases: list[str]
        self.summary: str
        self.rating: Rating
        self.tags: list[Tag]
        self.infobox: list[tuple[str, str | list[str]]]


class Tag:
    def __init__(self, name: str, count: int):
        self.name: str = name
        self.count: int = count

    def __repr__(self):
        return f"Tag(name={self.name}, count={self.count})"


class Rating:
    def __init__(
        self, score: float = -1, count: dict[str, int] | None = None, total: int = -1
    ):
        self.score: float = score
        self.total: int = total
        self.count: dict[str, int] = (
            count
            if count is not None
            else {
                "1": 0,
                "2": 0,
                "3": 0,
                "4": 0,
                "5": 0,
                "6": 0,
                "7": 0,
                "8": 0,
                "9": 0,
                "10": 0,
            }
        )

    def __str__(self):
        score = str(self.score) if self.score > 0 else "n/a"
        total = str(self.total) if self.total > 0 else "n/a"
        return f"{score} ({total})"
