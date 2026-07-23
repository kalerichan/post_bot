import json
import os
from datetime import datetime

DB_PATH = 'data/database.json'


class Database:
    def __init__(self):
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        if not os.path.exists(DB_PATH):
            with open(DB_PATH, 'w', encoding='utf-8') as f:
                json.dump({"users": {}}, f, ensure_ascii=False, indent=2)

    def _read_db(self):
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _write_db(self, data):
        with open(DB_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_user_data(self, user_id):
        data = self._read_db()
        return data["users"].get(str(user_id), {})

    def save_user_data(self, user_id, user_data):
        data = self._read_db()
        data["users"][str(user_id)] = user_data
        self._write_db(data)

    def add_channel(self, user_id, channel_username):
        data = self._read_db()

        if str(user_id) not in data["users"]:
            data["users"][str(user_id)] = {"channels": []}

        channels = data["users"][str(user_id)].get("channels", [])
        if channel_username not in channels:
            channels.append(channel_username)
            data["users"][str(user_id)]["channels"] = channels

        self._write_db(data)

    def get_user_channels(self, user_id):
        user_data = self.get_user_data(user_id)
        return user_data.get("channels", [])

    def save_draft_post(self, user_id, post_data):
        user_data = self.get_user_data(user_id)
        user_data["current_draft"] = post_data
        self.save_user_data(user_id, user_data)

    def get_draft_post(self, user_id):
        user_data = self.get_user_data(user_id)
        return user_data.get("current_draft")


db = Database()