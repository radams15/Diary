import json
import os

from encryption import Crypt
from record import Record

class Storage:
    def __init__(self, file: str, crypt: Crypt, save_crypt=True):
        self.file = file
        self.json_data = []
        self.crypt = crypt
        self.save_crypt = save_crypt

        if not os.path.exists(self.file):
            self._refresh_save()

        try:
            self.load()
        except json.JSONDecodeError:
            print("DECODE ERROR")
            exit()

    def _refresh_save(self):
        json.dump([], open(self.file, "w"))

    def load(self):
        with open(self.file, "r") as file:
            raw_data = file.read()
            data = self.crypt.decrypt(raw_data)
            self.json_data = json.loads(data)

    def read(self):
        self.load()
        data = self.json_data
        return [Record.from_list(r) for r in data]

    def read_date(self, date: float):
        self.load()
        for r in self.json_data:
            if r[0] == date:
                return Record.from_list(r)
        return None

    def save(self):
        with open(self.file, "w") as file:
            data = json.dumps(self.json_data)
            if self.save_crypt:
                data = self.crypt.encrypt(data)
            file.write(data)

        
    def save_record(self, record: Record):
        self.load()
        self.json_data.append(record.to_list())
        self.save()


    def update_record(self, record: Record, new_record: Record):
        self.load()

        for i, j in enumerate(self.json_data):
            if j[0] == record.date.timestamp():
                self.json_data[i] = new_record.to_list()

        self.save()
        self.load()

    def delete_record(self, record:Record):
        self.load()

        for i, j in enumerate(self.json_data):
            if j[0] == record.date.timestamp():
                del self.json_data[i]
        self.save()