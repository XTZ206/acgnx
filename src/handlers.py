from abc import ABC, abstractmethod
import requests
import sqlite3
import json
from subjects import Subject, Rating, Tag


class SubjectHandler(ABC):
    @abstractmethod
    def fetch_subject(self, subject_id) -> Subject:
        pass

    @abstractmethod
    def search_subjects(self, keyword) -> list[Subject]:
        pass


class APIHandler(SubjectHandler):
    def __init__(self):
        self.headers = {"User-Agent": "XTZ206/acgnx/0.0.1"}

    @staticmethod
    def get_subject_from_json(subject_json: dict) -> Subject:
        subject = Subject()
        subject.id = subject_json["id"]
        subject.name = subject_json["name"]
        subject.type = {1: "BOOK", 2: "ANIME", 3: "MUSIC", 4: "GAME", 6: "REAL"}.get(
            subject_json["type"], "OTHER"
        )
        subject.date = subject_json["date"]

        subject.aliases = (
            [subject_json["name_cn"]] if subject_json["name_cn"] != "" else []
        )
        subject.summary = subject_json["summary"]
        subject.rating = Rating(
            subject_json["rating"]["score"],
            subject_json["rating"]["count"],
            subject_json["rating"]["total"],
        )

        subject.tags = []
        for tag_json in subject_json["tags"]:
            subject.tags.append(Tag(tag_json["name"], tag_json["count"]))

        subject.infobox = []
        for infoitem in subject_json["infobox"]:
            if infoitem["key"] == "中文名":
                if infoitem["value"] != "" and infoitem["value"] not in subject.aliases:
                    subject.aliases.append(infoitem["value"])
            if infoitem["key"] == "别名":
                for aliasitem in infoitem["value"]:
                    if aliasitem["v"] not in subject.aliases:
                        subject.aliases.append(aliasitem["v"])
            if isinstance(infoitem["value"], list):
                subject.infobox.append(
                    (infoitem["key"], [item["v"] for item in infoitem["value"]])
                )
            else:
                subject.infobox.append((infoitem["key"], [infoitem["value"]]))

        return subject

    def fetch_subject(self, subject_id) -> "Subject":
        response = requests.get(
            f"https://api.bgm.tv/v0/subjects/{subject_id}", headers=self.headers
        )
        return self.get_subject_from_json(response.json())

    def search_subjects(self, keyword: str) -> list[Subject]:
        response = requests.post(
            f"https://api.bgm.tv/v0/search/subjects?limit=10&offset=0",
            data=json.dumps({"keyword": keyword}),
            headers=self.headers,
        )
        return [
            self.get_subject_from_json(subject_json)
            for subject_json in response.json()["data"]
        ]


class DBHandler(SubjectHandler):
    def __init__(self, dbpath):
        self.connection = sqlite3.connect(dbpath)
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS SUBJECTS ("
            "ID INT, "
            "NAME TEXT NOT NULL, "
            "TYPE TEXT NOT NULL, "
            "DATE TEXT NOT NULL, "
            "ALIASES TEXT, "
            "SUMMARY TEXT, "
            "RATING TEXT, "
            "TAGS TEXT, "
            "INFOBOX TEXT, "
            "PRIMARY KEY (ID)"
            ")"
        )

    def __del__(self):
        self.connection.close()

    @staticmethod
    def get_aliases_from_field(field: str | None) -> list[str]:
        if field is None:
            return []
        return json.loads(field)

    @staticmethod
    def get_aliases_field_from_subject(subject: Subject) -> str:
        return json.dumps(subject.aliases, ensure_ascii=False)

    @staticmethod
    def get_summary_from_field(field: str | None) -> str:
        if field is None:
            return ""
        return field

    @staticmethod
    def get_summary_field_from_subject(subject: Subject) -> str:
        if subject.summary == "":
            return None
        return subject.summary

    @staticmethod
    def get_rating_from_field(field: str | None) -> Rating:
        if field is None:
            return Rating()
        rating_json = json.loads(field)
        return Rating(rating_json["score"], rating_json["count"], rating_json["total"])

    @staticmethod
    def get_rating_field_from_subject(subject: Subject) -> str:
        return json.dumps(
            {
                "score": subject.rating.score,
                "count": subject.rating.count,
                "total": subject.rating.total,
            }
        )

    @staticmethod
    def get_tags_from_field(field: str | None) -> list[Tag]:
        if field is None:
            return []
        return [
            Tag(tag_json["name"], tag_json["count"]) for tag_json in json.loads(field)
        ]

    @staticmethod
    def get_tags_field_from_subject(subject: Subject) -> str:
        return json.dumps(
            [{"name": tag.name, "count": tag.count} for tag in subject.tags],
            ensure_ascii=False,
        )

    @staticmethod
    def get_infobox_from_field(field: str | None) -> list[tuple[str, str]]:
        if field is None:
            return []
        return [(item[0], item[1]) for item in json.loads(field)]

    @staticmethod
    def get_infobox_field_from_subject(subject: Subject) -> str:
        return json.dumps(subject.infobox, ensure_ascii=False)

    def fetch_subject(self, subject_id: int) -> Subject:
        subject = Subject(subject_id)
        subject.name, subject.type, subject.date = self.connection.execute(
            "SELECT NAME, TYPE, DATE FROM SUBJECTS WHERE ID = ? ", (subject_id,)
        ).fetchone()
        subject.aliases = self.get_aliases_from_field(
            self.connection.execute(
                "SELECT ALIASES FROM SUBJECTS WHERE ID = ?", (subject_id,)
            ).fetchone()[0]
        )
        subject.summary = self.get_summary_from_field(
            self.connection.execute(
                "SELECT SUMMARY FROM SUBJECTS WHERE ID = ?", (subject_id,)
            ).fetchone()[0]
        )
        subject.rating = self.get_rating_from_field(
            self.connection.execute(
                "SELECT RATING FROM SUBJECTS WHERE ID = ?", (subject_id,)
            ).fetchone()[0]
        )
        subject.tags = self.get_tags_from_field(
            self.connection.execute(
                "SELECT TAGS FROM SUBJECTS WHERE ID = ?", (subject_id,)
            ).fetchone()[0]
        )
        subject.infobox = self.get_infobox_from_field(
            self.connection.execute(
                "SELECT INFOBOX FROM SUBJECTS WHERE ID = ?", (subject_id,)
            ).fetchone()[0]
        )
        return subject

    def fetch_all_subjects(self) -> list[Subject]:
        subjects = [
            Subject(subject_id)
            for subject_id, in self.connection.execute(
                "SELECT ID FROM SUBJECTS"
            ).fetchall()
        ]
        for subject in subjects:
            subject.name, subject.type, subject.date = self.connection.execute(
                "SELECT NAME, TYPE, DATE FROM SUBJECTS WHERE ID = ? ", (subject.id,)
            ).fetchone()
            subject.aliases = self.get_aliases_from_field(
                self.connection.execute(
                    "SELECT ALIASES FROM SUBJECTS WHERE ID = ?", (subject.id,)
                ).fetchone()[0]
            )
            subject.summary = self.get_summary_from_field(
                self.connection.execute(
                    "SELECT SUMMARY FROM SUBJECTS WHERE ID = ?", (subject.id,)
                ).fetchone()[0]
            )
            subject.rating = self.get_rating_from_field(
                self.connection.execute(
                    "SELECT RATING FROM SUBJECTS WHERE ID = ?", (subject.id,)
                ).fetchone()[0]
            )
            subject.tags = self.get_tags_from_field(
                self.connection.execute(
                    "SELECT TAGS FROM SUBJECTS WHERE ID = ?", (subject.id,)
                ).fetchone()[0]
            )
            subject.infobox = self.get_infobox_from_field(
                self.connection.execute(
                    "SELECT INFOBOX FROM SUBJECTS WHERE ID = ?", (subject.id,)
                ).fetchone()[0]
            )
        return subjects

    def search_subjects(self, keyword: str) -> list[Subject]:
        subjects = [
            Subject(subject_id)
            for subject_id, in self.connection.execute(
                "SELECT ID FROM SUBJECTS WHERE NAME LIKE ? OR ALIASES LIKE ?",
                (f"%{keyword}%", f"%{keyword}%"),
            ).fetchall()
        ]
        for subject in subjects:
            subject.name, subject.type, subject.date = self.connection.execute(
                "SELECT NAME, TYPE, DATE FROM SUBJECTS WHERE ID = ? ", (subject.id,)
            ).fetchone()
            subject.aliases = self.get_aliases_from_field(
                self.connection.execute(
                    "SELECT ALIASES FROM SUBJECTS WHERE ID = ?", (subject.id,)
                ).fetchone()[0]
            )
            subject.summary = self.get_summary_from_field(
                self.connection.execute(
                    "SELECT SUMMARY FROM SUBJECTS WHERE ID = ?", (subject.id,)
                ).fetchone()[0]
            )
            subject.rating = self.get_rating_from_field(
                self.connection.execute(
                    "SELECT RATING FROM SUBJECTS WHERE ID = ?", (subject.id,)
                ).fetchone()[0]
            )
            subject.tags = self.get_tags_from_field(
                self.connection.execute(
                    "SELECT TAGS FROM SUBJECTS WHERE ID = ?", (subject.id,)
                ).fetchone()[0]
            )
            subject.infobox = self.get_infobox_from_field(
                self.connection.execute(
                    "SELECT INFOBOX FROM SUBJECTS WHERE ID = ?", (subject.id,)
                ).fetchone()[0]
            )
        return subjects

    def update_subjects(self, *subjects: Subject):
        for subject in subjects:
            self.connection.execute(
                "UPDATE SUBJECTS SET NAME = ?, TYPE = ?, DATE = ? WHERE ID = ?",
                (subject.name, subject.type, subject.date, subject.id),
            )
            self.connection.execute(
                "UPDATE SUBJECTS SET ALIASES = ? WHERE ID = ?",
                (self.get_aliases_field_from_subject(subject), subject.id),
            )
            self.connection.execute(
                "UPDATE SUBJECTS SET SUMMARY = ? WHERE ID = ?",
                (self.get_summary_field_from_subject(subject), subject.id),
            )
            self.connection.execute(
                "UPDATE SUBJECTS SET RATING = ? WHERE ID = ?",
                (self.get_rating_field_from_subject(subject), subject.id),
            )
            self.connection.execute(
                "UPDATE SUBJECTS SET TAGS = ? WHERE ID = ?",
                (self.get_tags_field_from_subject(subject), subject.id),
            )
            self.connection.execute(
                "UPDATE SUBJECTS SET INFOBOX = ? WHERE ID = ?",
                (self.get_infobox_field_from_subject(subject), subject.id),
            )
        self.connection.commit()

    def insert_subjects(self, *subjects: Subject):
        for subject in subjects:
            self.connection.execute(
                "REPLACE INTO SUBJECTS (ID, NAME, TYPE, DATE) VALUES (?, ?, ?, ?)",
                (subject.id, subject.name, subject.type, subject.date),
            )
            self.connection.execute(
                "UPDATE SUBJECTS SET ALIASES = ? WHERE ID = ?",
                (self.get_aliases_field_from_subject(subject), subject.id),
            )
            self.connection.execute(
                "UPDATE SUBJECTS SET SUMMARY = ? WHERE ID = ?",
                (self.get_summary_field_from_subject(subject), subject.id),
            )
            self.connection.execute(
                "UPDATE SUBJECTS SET RATING = ? WHERE ID = ?",
                (self.get_rating_field_from_subject(subject), subject.id),
            )
            self.connection.execute(
                "UPDATE SUBJECTS SET TAGS = ? WHERE ID = ?",
                (self.get_tags_field_from_subject(subject), subject.id),
            )
            self.connection.execute(
                "UPDATE SUBJECTS SET INFOBOX = ? WHERE ID = ?",
                (self.get_infobox_field_from_subject(subject), subject.id),
            )
        self.connection.commit()

    def delete_subjects(self, *subjects: Subject):
        for subject in subjects:
            self.connection.execute("DELETE FROM SUBJECTS WHERE ID = ?", (subject.id,))
        self.connection.commit()
