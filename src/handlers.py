from abc import ABC, abstractmethod
import requests
import sqlite3
import json
import subjects
from subjects import Subject


class SubjectHandler(ABC):
    @abstractmethod
    def fetch_subject(self, subject_id) -> "Subject":
        pass
    @abstractmethod
    def search_subjects(self, keyword) -> list["Subject"]:
        pass


class APIHandler(SubjectHandler):
    def __init__(self):
        self.headers = {
            "User-Agent": "XTZ206/acgnx/0.0.1"
        }
        self.subject_factory = subjects.SubjectFactory()
    
    def fetch_subject(self, subject_id) -> "Subject":
        response = requests.get(f"https://api.bgm.tv/v0/subjects/{subject_id}", headers=self.headers)
        return self.subject_factory.get_subject_from_json(response.json())    

    def search_subjects(self, keyword: str) -> list[Subject]:
        response = requests.post(
            f"https://api.bgm.tv/v0/search/subjects?limit=10&offset=0",
            data=json.dumps({"keyword": keyword}), headers=self.headers
        )
        return [self.subject_factory.get_subject_from_json(subject_json) for subject_json in response.json()["data"]]


class DBHandler(SubjectHandler):
    def __init__(self, dbpath):
        self.connection = sqlite3.connect(dbpath)
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS SUBJECTS ("
            "ID INT PRIMARY KEY, "
            "NAME TEXT, "
            "ALIASES TEXT, "
            "TYPE TEXT, "
            "DATE TEXT, "
            "RATING REAL, "
            "SUMMARY TEXT, "
            "INFOBOX TEXT, "
            "PRIMARY KEY(ID)"
            ")"
        )


        self.cursor = self.connection.cursor()
        self.subject_factory = subjects.SubjectFactory()
    
    def __del__(self):
        self.connection.close()

    @staticmethod
    def convert_items(items: list[str]) -> str:
        return "\n".join(items)

    @staticmethod
    def convert_pairs(pairs: list[tuple[str, str]]) -> str:
        return "\n".join([f"{pair[0]}: {pair[1]}" for pair in pairs])

    def fetch_subject(self, subject_id: int) -> Subject:
        row = self.connection.execute(
            "SELECT ID, NAME, ALIASES, TYPE, DATE, RATING, SUMMARY, INFOBOX FROM SUBJECTS WHERE ID = ?",
            (subject_id,)
        ).fetchone()
        return self.subject_factory.get_subject_from_row(row)
    
    def search_subjects(self, keyword: str) -> list[Subject]:
        subjects = []
        rows = self.connection.execute(
            "SELECT ID, NAME, ALIASES, TYPE, DATE, RATING, SUMMARY, INFOBOX, FROM SUBJECTS WHERE NAME LIKE ? OR ALIASES LIKE ?",
            (f"%{keyword}%", f"%{keyword}%")
        ).fetchall()
        for row in rows:
            subject = self.subject_factory.get_subject_from_row(row)
            if subject is not None:
                subjects.append(subject)
        return subjects

    def fetch_all_subjects(self) -> list[Subject]:
        subjects = []
        rows = self.connection.execute("SELECT ID, NAME, ALIASES, TYPE, DATE, RATING, SUMMARY, INFOBOX FROM SUBJECTS").fetchall()
        for row in rows:
            subject = self.subject_factory.get_subject_from_row(row)
            if subject is not None:
                subjects.append(subject)
        return subjects

    def update_subjects(self, subjects: list[Subject]):
        for subject in subjects:
            self.connection.execute(
                "UPDATE SUBJECTS SET NAME = ?, TYPE = ?, DATE = ?, RATING = ? WHERE ID = ?", 
                (subject.name, subject.type, subject.date, subject.rating, subject.id)
            )
            self.connection.execute("UPDATE SUBJECTS SET ALIASES = ? WHERE ID = ?", ("\n".join(subject.aliases), subject.id))
            self.connection.execute("UPDATE SUBJECTS SET SUMMARY = ? WHERE ID = ?", (subject.summary, subject.id))
            self.connection.execute("UPDATE SUBJECTS SET INFOBOX = ? WHERE ID = ?", (json.dumps(subject.infobox, ensure_ascii=False, indent=4), subject.id))

        self.connection.commit()
    
    def insert_subjects(self, subjects: list[Subject]):
        for subject in subjects:
            self.connection.execute(
                "INSERT INTO SUBJECTS (ID, NAME, TYPE, DATE, RATING) VALUES (?, ?, ?, ?, ?)",
                (subject.id, subject.name, subject.type, subject.date, subject.rating)
            )
            self.connection.execute("UPDATE SUBJECTS SET ALIASES = ? WHERE ID = ?", ("\n".join(subject.aliases), subject.id))
            self.connection.execute("UPDATE SUBJECTS SET SUMMARY = ? WHERE ID = ?", (subject.summary, subject.id))
            self.connection.execute("UPDATE SUBJECTS SET INFOBOX = ? WHERE ID = ?", (json.dumps(subject.infobox, ensure_ascii=False, indent=4), subject.id))
        self.connection.commit()
        