from datetime import datetime

class Record:
    def __init__(self, date: float, title: str, body: str):
        self.date = datetime.fromtimestamp(date)
        self.title = title
        self.body = body

    @staticmethod
    def from_list(data: list):
        return Record(data[0], data[1], data[2])

    def format_date(self, date_format="%A %B %-d %Y"):
        return self.date.strftime(date_format)

    def format(self):
        return [self.format_date(), self.title, self.body]

    def to_list(self):
        return [self.date.timestamp(), self.title, self.body]