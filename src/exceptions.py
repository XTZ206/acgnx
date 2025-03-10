from subjects import Subject

class SubjectNotFoundError(Exception):
    def __init__(self, subject: Subject, dbname: str = "database"):
        self.subject = subject
        super().__init__(f"Subject {subject.id} not found in {dbname}")