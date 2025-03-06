from abc import ABC
import json

class SubjectFactory:
    @staticmethod
    def get_subject_from_json(subject_json: dict) -> "Subject":
        subject = Subject()
        subject.id = subject_json["id"]
        subject.name = subject_json["name"]
        subject.aliases = [subject_json["name_cn"]] if subject_json["name_cn"] != "" else []
        subject.type = {
            1: "BOOK",
            2: "ANIME",
            3: "MUSIC",
            4: "GAME",
            6: "REAL"
        }.get(subject_json["type"], "Unknown")
        subject.date = subject_json["date"]
        subject.rating = subject_json["rating"]["score"]
        subject.summary = subject_json["summary"]
        subject.infobox = []

        for infoitem in subject_json["infobox"]:
            if infoitem["key"] == "别名":
                for aliasitem in infoitem["value"]:
                    subject.aliases.append(aliasitem["v"])
            if isinstance(infoitem["value"], list):
                subject.infobox.append((infoitem["key"], [item["v"] for item in infoitem["value"]]))
            else:
                subject.infobox.append((infoitem["key"], [infoitem["value"]]))


        return subject
    
    @staticmethod
    def get_subject_from_row(row) -> "Subject":
        # row[0] ID field
        # row[1] NAME field
        # row[2] ALIASES field
        # row[3] TYPE field
        # row[4] DATE field
        # row[5] RATING field
        # row[6] SUMMARY field
        # row[7] INFOBOX field

        subject = Subject()
        subject.id = row[0]
        subject.name = row[1]
        subject.aliases = row[2].split("\n") if row[2] != "" else []
        subject.type = row[3]
        subject.date = row[4]
        subject.rating = row[5]
        subject.summary = row[6]
        subject.infobox = json.loads(row[7]) if row[7] != "" and row[7] is not None else {}

        return subject

class Subject:
    def __init__(self, id=None):
        self.id: int = id
        self.name: str
        self.aliases: list[str] = []
        self.type: str
        self.date: str
        self.rating: float
        self.summary: str
        self.infobox: list[tuple] = []

    def copy(self, other: "Subject"):
        self.id = other.id
        self.name = other.name
        self.aliases = other.aliases
        self.type = other.type
        self.date = other.date
        self.rating = other.rating
        self.summary = other.summary
        self.infobox = other.infobox