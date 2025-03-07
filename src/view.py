from typing import Literal
import subjects
from subjects import Subject
import handlers
from handlers import SubjectHandler


class Viewer:
    def __init__(
        self,
        subjects: list[Subject] = None,
        updater: "Updater" = None,
        selector: "Selector" = None,
    ):
        self.subjects = subjects if subjects is not None else []
        self.updater: "Updater" = updater if updater is not None else Updater()
        self.selector: "Selector" = selector if selector is not None else Selector()

    def list_subjects(self):
        id_width = 6
        type_width = 6
        date_width = 10
        rate_width = 12
        name_width = 30
        print(
            "ID".center(id_width),
            "TYPE".center(type_width),
            "DATE".center(date_width),
            "RATE".center(rate_width),
            "NAME".center(name_width),
        )
        print(
            "-" * id_width,
            "-" * type_width,
            "-" * date_width,
            "-" * rate_width,
            "-" * name_width,
        )
        for subject in self.subjects:
            print(
                str(subject.id).rjust(id_width),
                str(subject.type).center(type_width),
                str(subject.date).center(date_width),
                str(subject.rating).ljust(rate_width),
                str(subject.name).ljust(name_width),
            )

    def view_subject(self):
        subject = self.subjects[0]
        print("ID:", subject.id)
        print("NAME:", subject.name)
        print("TYPE:", subject.type)
        print("DATE:", subject.date)
        
        print("ALIASES:")
        print(*subject.aliases, sep="\n")
        print("SUMMARY:") 
        print(subject.summary)
        print("RATING:", subject.rating)
        print("TAGS:")
        print(*sorted(subject.tags, key=lambda x: x.count, reverse=True), sep=" / ")
        print("INFOBOX:")
        for key, value in subject.infobox:
            if isinstance(value, list):
                print(f"{key}:", "/".join(value))
            else:
                print(f"{key}:", value)

    def update_subjects(self):
        for index, subject in enumerate(self.subjects):
            self.subjects[index] = self.updater.fetch(subject)

    def search_subjects(self, keyword: str):
        self.subjects = self.updater.search(keyword)


class Updater:
    def __init__(self, handler: SubjectHandler | None = None):
        self.handler: SubjectHandler | None = handler

    def fetch(self, subject: Subject) -> Subject:
        if self.handler is None:
            return subject
        return self.handler.fetch_subject(subject.id)

    def search(self, keyword: str) -> list[Subject]:
        if self.handler is None:
            return []
        return self.handler.search_subjects(keyword)


class Selector:
    def __init__(self):
        pass

    def select(self, subjects: list[Subject]):
        while True:
            match input("Select a subject to dump: "):
                case "1":
                    return subjects[0]
                case "2":
                    return subjects[1]
                case "3":
                    return subjects[2]
                case "4":
                    return subjects[3]
                case "q":
                    return None

        return subjects[index]
