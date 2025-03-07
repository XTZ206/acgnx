from abc import ABC
import json


class Subject:
    """
    A class to represent a subject.

    Attributes:
    ----------
    id : int
        The unique identifier for the subject.
    name : str
        The name of the subject.
    type : str
        The type/category of the subject.
    date : str
        The date associated with the subject.
    aliases : list[str]
        A list of alternative names for the subject.
    summary : str
        A brief summary or description of the subject.
    rating : Rating
        The rating of the subject.
    tags : list[Tag]
        A list of tags associated with the subject.
    infobox : list[tuple[str, str | list[str]]]
        A list of key-value pairs containing additional information about the subject.

    Methods:
    -------
    __init__(self, id: int = -1):
        Initializes the Subject with an optional id.
    """

    def __init__(self, id: int = -1):
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

    def __str__(self):
        return f"{self.name} ({self.count})"

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
        if self.score > 0 and self.total > 0:
            return f"{self.score:.1f} ({self.total})"
        elif self.score > 0:
            return f"{self.score:.1f}"
        elif self.score == 0 and self.total == 0:
            return "unrated"
        else:
            return "unknown"
