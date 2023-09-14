from PySide2.QtWidgets import QApplication, QDialog, QFileDialog
from PySide2.QtUiTools import QUiLoader
from PySide2 import QtCore
from notes_model import DataModel
import sys
import os
import json


class SettingsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.base_directory = os.getcwd()
        self.dm = DataModel()

        loader = QUiLoader()
        ui_file = QtCore.QFile("settingsWidget.ui")
        ui_file.open(QtCore.QFile.ReadOnly)
        self.window = loader.load(ui_file)
        ui_file.close()

        self.setWindowTitle('Settings')
        self.dm.load_settings_from_json()

        self.export_directory = self.dm.get_export_directory()
        self.window.export_location_text.setText(self.export_directory)

        self.setLayout(self.window.layout())
        self.setGeometry(0, 0, 600, 100)

        self.window.export_location_button.clicked.connect(self.json_to_text)
        self.window.export_location_folder_button.clicked.connect(self.show_export_folder_dialog)

        self.window.apply_button.clicked.connect(self.apply_settings)
        self.window.cancel_button.clicked.connect(self.cancel_settings)

    def load_settings(self):
        self.dm.load_settings_from_json()
        self.window.export_location_text.setText(self.export_directory)

    def update_export_directory(self):
        directory = self.window.export_location_text.text()
        self.dm.update_export_directory(directory)

    def apply_settings(self):
        self.update_export_directory()
        self.dm.save_settings_to_json()
        self.close()

    def cancel_settings(self):
        self.close()

    def show_export_folder_dialog(self):
        self.show_folder_dialog(self.window.export_location_text)

    def show_folder_dialog(self, line_edit):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        options |= QFileDialog.ShowDirsOnly

        initial_directory = line_edit.text()

        # Explicitly set the parent window for the dialog
        folder_path = QFileDialog.getExistingDirectory(self.window, "Select Folder", initial_directory, options=options)

        if folder_path:
            line_edit.setText(folder_path)

    def json_to_text(self):
        path = self.dm.path
        file_name = "Notes_data.json"
        file_path = os.path.join(path, file_name)
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)

        # Extract shots' text and task cards
        shots = data['shots']
        task_cards = data['task_cards']

        # Create a dictionary to store task cards under each shot's title
        shot_task_map = {}
        for shot in shots:
            shot_text = shot['text']
            shot_task_map[shot_text] = []

        for card in task_cards:
            associated_shot_id = card['associated_shot_id']
            for shot in shots:
                if shot['id'] == associated_shot_id:
                    shot_text = shot['text']
                    card_info = f"Note: {card['text']}, Urgent: {card['urgent']}, Completed: {card['completed']}"
                    shot_task_map[shot_text].append(card_info)

        # Create and write to the text file
        output_directory = self.window.export_location_text.text()
        output_file_path = os.path.join(output_directory, 'converted_notes.txt')
        with open(output_file_path, 'w') as text_file:
            for shot_text, cards in shot_task_map.items():
                text_file.write(f"Shot: {shot_text}\n")
                if cards:
                    text_file.write('\n'.join(cards) + '\n')
                text_file.write('\n')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SettingsWindow()
    window.show()
    sys.exit(app.exec_())
