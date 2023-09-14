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
        self.filter_states = {category: {item: False for item in items} for category, items in self.filter_dict.items()}

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

    def get_task_cards(self, filter_shot_id=None):
        if filter_shot_id is not None:
            filtered_task_cards = [task_card for task_card in self.task_cards if
                                   task_card.associated_shot_id == filter_shot_id]
            return filtered_task_cards
        else:
            return self.task_cards

    def get_task_cards_todo(self, filter_shot_id=None):
        todo_task_cards = []

        for task_card in self.task_cards:
            if (filter_shot_id and task_card.associated_shot_id != filter_shot_id) or task_card.completed:
                continue
            todo_task_cards.append(task_card)

        return todo_task_cards

    def get_task_cards_completed(self, filter_shot_id=None):
        completed_task_cards = []

        for task_card in self.task_cards:
            if task_card.completed:
                if filter_shot_id is None or task_card.associated_shot_id == filter_shot_id:
                    completed_task_cards.append(task_card)

        return completed_task_cards

    def get_task_cards_urgent(self, filter_shot_id=None):
        urgent_task_cards = []

        for task_card in self.task_cards:
            if task_card.urgent:
                if filter_shot_id is None or task_card.associated_shot_id == filter_shot_id:
                    urgent_task_cards.append(task_card)

        return urgent_task_cards

    def get_task_cards_date(self, filter_shot_id=None, filter_date=None):
        date_task_cards = []
        filter_state = self.current_filter_index

        current_datetime = datetime.now().date()

        # Calculate the start and end of the previous week
        day_of_week = current_datetime.weekday()
        start_of_previous_week = current_datetime - timedelta(days=day_of_week + 7)
        end_of_previous_week = start_of_previous_week + timedelta(days=6)

        # Define a mapping of filter_state to corresponding functions
        filter_functions = {
            0: self.get_task_cards_todo,
            1: self.get_task_cards_urgent,
            2: self.get_task_cards_completed,
            3: self.get_task_cards,
        }

        # Get the appropriate task cards based on filter_state and filter_shot_id
        task_cards = filter_functions.get(filter_state, self.get_task_cards)(filter_shot_id)

        for task_card in task_cards:
            card_date = datetime.strptime(task_card.time_created, "%d/%m/%Y %H:%M:%S").date()

            if filter_date == 0 and card_date == current_datetime:
                date_task_cards.append(task_card)
            elif filter_date == 1 and card_date == (current_datetime - timedelta(days=1)):
                date_task_cards.append(task_card)
            elif filter_date == 2:
                if start_of_previous_week <= card_date <= end_of_previous_week:
                    date_task_cards.append(task_card)
            elif filter_date == 3:
                date_task_cards.append(task_card)

        return date_task_cards

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

        # Print the filter states at the end
        print("Filter States:")
        for category, items in self.filter_states.items():
            for item, state in items.items():
                print(f"{category} - {item}: {state}")

    def reset_filter_states(self):
        for category, items in self.filter_states.items():
            for item in items:
                self.filter_states[category][item] = False




