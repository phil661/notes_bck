import random
import string
import json
import os
import getpass
import datetime
from datetime import datetime, timedelta


class TaskCard:
    def __init__(self, text, completed, urgent, id, associated_shot_id, index, time_created):
        self.text = text
        self.urgent = urgent
        self.completed = completed
        self.index = index
        self.id = id
        self.associated_shot_id = associated_shot_id
        self.time_created = time_created


class Shot:
    def __init__(self, text, id):
        self.text = text
        self.id = id


class DataModel:
    filter_states = None

    def __init__(self):
        self.current_user = getpass.getuser()

        self.task_cards = []
        self.shot_list = []
        self.index = None

        self.urgent_button_state = False
        self.burger_button_state = False
        self.current_filter_index = 0
        self.current_date_filter = 0
        self.current_shot = None

        self.base_directory = os.getcwd()

        self.path = os.path.expanduser(f"~{self.current_user}/.nuke/Notes")
        self.export_directory = self.path

        self.filter_dict = {
            "Status": ["To Do", "Urgent", "Completed"],
            "Date Created": ["Today", "Yesterday", "Last Week"]
        }

        # Initialize filter_states if it's None (first instance)
        if DataModel.filter_states is None:
            DataModel.filter_states = {category: {item: False for item in items} for category, items in
                                       self.filter_dict.items()}

    def create_task_card(self, text, associated_shot_id):
        id = self.generate_random_id()
        time_created = self.get_current_date_and_time()
        completed = False
        urgent = self.urgent_button_state
        index = len(self.task_cards)  # Calculate the index based on the current number of task cards
        self.add_task_card(text, completed, urgent, id, associated_shot_id, index, time_created)

    def add_task_card(self, text, completed, urgent, id, associated_shot_id, index, time_created):
        self.task_cards.append(TaskCard(text, completed, urgent, id, associated_shot_id, index, time_created))
        self.index = index

    def update_task_card_text(self, task_card_id, new_text):
        for task_card in self.task_cards:
            if task_card.id == task_card_id:
                task_card.text = new_text
                break

    def update_task_card_index(self, task_text, new_index):
        for task_card in self.task_cards:
            if task_card.text == task_text:
                task_card.index = new_index

    def delete_task_card(self, task_card_id):
        task_card_to_delete = None

        for task_card in self.task_cards:
            if task_card.id == task_card_id:
                task_card_to_delete = task_card
                break

        if task_card_to_delete:
            self.task_cards.remove(task_card_to_delete)

    def create_shot(self, text):
        id = self.generate_random_id()
        self.add_shot(text, id)

    def add_shot(self, text, id):
        self.shot_list.append(Shot(text, id))

    def is_shot_duplicate(self, text):
        existing_shots = [shot.text.lower() for shot in self.shot_list]
        return text.lower() in existing_shots

    def get_shot_list(self):
        return self.shot_list

    def delete_shot(self, shot_id):
        task_cards_to_delete = []

        # Collect task cards associated with the shot
        for task_card in self.task_cards:
            if task_card.associated_shot_id == shot_id:
                task_cards_to_delete.append(task_card)

        # Remove collected task cards
        for task_card in task_cards_to_delete:
            self.task_cards.remove(task_card)

        # Remove the shot itself
        shot_to_delete = None
        for shot in self.shot_list:
            if shot.id == shot_id:
                shot_to_delete = shot
                break

        if shot_to_delete:
            self.shot_list.remove(shot_to_delete)

    def update_shot_name(self, shot_id, new_name):
        for shot in self.shot_list:
            if shot.id == shot_id:
                shot.text = new_name
                break

    def generate_random_id(self):
        id_length = 8
        characters = string.ascii_letters + string.digits
        while True:
            new_id = ''.join(random.choice(characters) for _ in range(id_length))
            if not any(task_card.id == new_id for task_card in self.task_cards):
                return new_id

    @staticmethod
    def get_current_date_and_time():
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        return dt_string

    @staticmethod
    def get_current_date():
        now = datetime.now()
        date_string = now.strftime("%d/%m/%Y")
        return date_string

    def get_task_cards(self, filter_shot_id=None):
        if filter_shot_id is not None:
            filtered_task_cards = [task_card for task_card in self.task_cards if
                                   task_card.associated_shot_id == filter_shot_id]
            return filtered_task_cards
        else:
            return self.task_cards

    def get_task_cards_filtered(self, filter_shot_id=None):
        # TODO: make the shot_id work.
        status_filtered = []
        filtered_task_cards = []

        today_date = self.get_current_date()
        yesterday_date = (datetime.now() - timedelta(days=1)).strftime("%d/%m/%Y")
        # TODO: create the last week filter

        status_filter = self.filter_states.get("Status")
        date_filter = self.filter_states.get("Date Created")

        # Filter by Status
        selected_filters_status = [item for item in self.filter_dict.get("Status", []) if
                                   status_filter.get(item, False)]

        for task_card in self.task_cards:
            if filter_shot_id is not None and task_card.associated_shot_id != filter_shot_id:
                continue

            if (
                    ("To Do" in selected_filters_status and not task_card.completed) or
                    ("Urgent" in selected_filters_status and task_card.urgent and not task_card.completed) or
                    ("Completed" in selected_filters_status and task_card.completed)
            ):
                status_filtered.append(task_card)

        # Filter by Date Created

        selected_filters_date = [item for item in self.filter_dict.get("Date Created", []) if
                                 date_filter.get(item, False)]

        for task_card in status_filtered if status_filtered else self.task_cards:
            if (
                    ("Today" in selected_filters_date and task_card.time_created.startswith(today_date)) or
                    ("Yesterday" in selected_filters_date and task_card.time_created.startswith(yesterday_date))
            ):
                filtered_task_cards.append(task_card)

        if filtered_task_cards:
            return filtered_task_cards
        elif status_filtered:
            return status_filtered
        else:
            return self.task_cards

    def toggle_completed(self, task_id):
        for task_card in self.task_cards:
            if task_card.id == task_id:
                task_card.completed = not task_card.completed

    def toggle_urgent(self, task_id):
        for task_card in self.task_cards:
            if task_card.id == task_id:
                task_card.urgent = not task_card.urgent

    def save_data_to_json(self):
        file_name = "Notes_data.json"
        file_path = os.path.join(self.path, file_name)

        if not os.path.exists(self.path):
            os.mkdir(self.path)

        data = {
            "task_cards": [task_card.__dict__ for task_card in self.task_cards],
            "shots": [shot.__dict__ for shot in self.shot_list],
            "user_preferences": {
                "current_shot": self.current_shot,
                "current_filter_index": self.current_filter_index,
                "current_date_filter": self.current_date_filter,
                "urgent_button_state": self.urgent_button_state,
                "filter_dict": self.filter_dict,
            }
        }

        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)

    def load_data_from_json(self):
        file_name = "Notes_data.json"
        file_path = os.path.join(self.path, file_name)
        try:
            with open(file_path, "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            data = {"task_cards": [], "shots": [], "user_preferences": {}}

        self.task_cards = [TaskCard(**task_card_data) for task_card_data in data["task_cards"]]
        self.shot_list = [Shot(**shot_data) for shot_data in data["shots"]]

        # Load user preferences
        user_preferences = data["user_preferences"]
        self.current_shot = user_preferences.get("current_shot", None)
        self.urgent_button_state = user_preferences.get("urgent_button_state", False)
        self.current_filter_index = user_preferences.get("current_filter_index", 0)
        self.current_date_filter = user_preferences.get("current_date_filter", 0)
        return data

    def update_export_directory(self, directory):
        self.export_directory = directory
        return directory

    def save_settings_to_json(self):
        file_name = "Notes_settings.json"
        file_path = os.path.join(self.path, file_name)

        if not (os.path.exists(self.path)):
            os.mkdir(self.path)

        settings = {
            "export_directory": self.export_directory
        }

        with open(file_path, "w") as file:
            json.dump(settings, file, indent=4)

    def load_settings_from_json(self):
        file_name = "Notes_settings.json"
        file_path = os.path.join(self.path, file_name)
        try:
            with open(file_path, "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            data = {"settings": {}}

        self.export_directory = data.get("export_directory")
        return data

    def get_export_directory(self):
        directory = self.export_directory
        if directory is None:
            directory = self.path
        return directory

    def get_filter_dict(self):
        return self.filter_dict

    def set_filter_states(self, category, item):
        if category in self.filter_states and item in self.filter_states[category]:
            # Toggle the state for the clicked item
            self.filter_states[category][item] = not self.filter_states[category][item]

    def reset_filter_states(self):
        for category, items in self.filter_states.items():
            for item in items:
                self.filter_states[category][item] = False
