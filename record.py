from datetime import datetime

DATE_FORMAT = "%A %B %d %Y"

class Record:
    def __init__(self, date, title: str, body: str):
        try:
            self.date = datetime.fromtimestamp(float(date))
        except:
            self.date = datetime.strptime(date, DATE_FORMAT)
        self.title = title
        self.body = body

    @staticmethod
    def from_list(data: list):
        return Record(data[0], data[1], data[2])

    def format_date(self):
        return self.date.strftime(DATE_FORMAT)

    def format(self):
        return [self.format_date(), self.title, self.body]

    def to_list(self):
        return [self.date.timestamp(), self.title, self.body]