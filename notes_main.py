from notes_model import TaskCardDataModel
from filter_window import SettingsWindow
from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QMessageBox, QLineEdit
from PySide2.QtCore import Qt


import sys
import os

try:
    import nuke
    import nukescripts
    import qtmodern.styles  # TODO: Will probably not work for everyone since they don't have it installed locally, would need to rez install it with pipeline
except:
    pass

#sys.path.append('/Volumes/Projects/Production/Personal/Plariviere/notes_app')
os.chdir("/Volumes/Projects/Production/Personal/Plariviere/notes_app")


class ClickableFrame(QtWidgets.QFrame):
    clicked = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def dropEvent(self, event):
        self.dropped.emit()
        super().dropEvent(event)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.dm = TaskCardDataModel()
        self.dm.load_settings_from_json()
        self.dm.load_data_from_json()

        loader = QUiLoader()
        ui_file = QtCore.QFile("mainWindow.ui")
        ui_file.open(QtCore.QFile.ReadOnly)
        self.window = loader.load(ui_file)
        ui_file.close()

        self.setWindowTitle('Notes')

        self.setCentralWidget(self.window)
        self.setGeometry(0, 0, 800, 600)
        self.move(QtGui.QCursor().pos() - QtCore.QPoint(400, 65))

        self.setup_connections()

        self.load_shot_list()
        self.load_data()

        self.load_task_cards()  # Populate task cards based on selected shot

        self.setup_context_menu()
        self.setup_shot_context_menu()
        self.setup_shortcuts()
        self.setup_stylesheet()

        #self.window.task_list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        #self.window.filter_tree.header().setVisible(False)

        try:
            if nuke:
                self.create_gustave_shot()
        except:
            pass

    def create_gustave_shot(self):
        shot_text = nuke.root().knob('g_entity_name').value()
        if shot_text:
            if not self.dm.is_shot_duplicate(shot_text):
                self.dm.create_shot(shot_text)
                self.window.add_shot_text.clear()
                self.load_shot_list()

                # Select the newly added shot in the list
                items = self.window.shot_list.findItems(shot_text, QtCore.Qt.MatchExactly)
                if items:
                    self.window.shot_list.setCurrentItem(items[0])

    def setup_stylesheet(self):
        self.window.shot_list.setStyleSheet("""
            QListWidget::item:selected {
                background-color: rgb(247, 147, 30);
                color: white;
            }
        """)

    def load_data(self):
        # Set UI elements' states based on loaded user preferences
        if self.dm.burger_button_state:
            self.window.burger_button.click()
        if self.dm.urgent_button_state:
            self.window.urgent_button.click()

        current_filter_index = self.dm.current_filter_index
        date_filter_index = self.dm.current_date_filter

        #self.window.filter_combobox.setCurrentIndex(current_filter_index)
        #self.window.date_filter_combobox.setCurrentIndex(date_filter_index)

        # load shot
        shot = self.window.shot_list.findItems(self.dm.current_shot, QtCore.Qt.MatchExactly)
        if shot:
            self.window.shot_list.setCurrentItem(shot[0])

    @staticmethod
    def load_item_widget():
        loader = QUiLoader()
        item_ui_file = QtCore.QFile("itemWidget.ui")
        item_ui_file.open(QtCore.QFile.ReadOnly)
        item_widget = loader.load(item_ui_file)
        item_ui_file.close()

        frame = item_widget.findChild(QtWidgets.QFrame, "frame")
        frame.setStyleSheet("""
                QFrame {
                    background-color: rgb(50, 50, 50);
                    border: none;
                }
            """)
        return item_widget

    def setup_connections(self):
        self.window.task_input_text.returnPressed.connect(self.create_task_card)
        self.window.add_shot_text.returnPressed.connect(self.create_shot)
        self.window.shot_list.currentItemChanged.connect(self.load_task_cards)
        self.window.shot_list.currentItemChanged.connect(self.update_current_shot)

        #self.window.filter_combobox.currentIndexChanged.connect(self.filter_combobox_changed)
        #self.window.date_filter_combobox.currentIndexChanged.connect(self.date_filter_combobox_changed)

        self.window.filters_button.clicked.connect(self.show_filters)

        self.window.task_list.itemPressed.connect(self.handle_frame_click)

        self.window.urgent_button.clicked.connect(self.urgent_button_clicked)
        self.window.task_list.itemClicked.connect(self.handle_item_clicked)  # Connect the signal

        self.window.text_search.textChanged.connect(self.task_search)

        self.window.shot_list.itemDoubleClicked.connect(self.rename_selected_shot)

        self.window.shot_search.textChanged.connect(self.shot_search)

        self.window.settings_button.clicked.connect(self.open_settings_window)
        self.window.settings_button.clicked.connect(self.dm.save_data_to_json)

    def show_filters(self):
        #current_state = self.window.filter_tree.isVisible()
        #self.window.filter_tree.setVisible(not current_state)
        pass

    def open_settings_window(self):
        self.settings_window = SettingsWindow(parent=self)  # Set parent to MainWindow
        self.settings_window.exec_()

    def filter_combobox_changed(self, index):
        self.dm.current_filter_index = index
        self.load_task_cards()

    def date_filter_combobox_changed(self, index):
        self.dm.current_date_filter = index
        self.load_task_cards()

    def task_search(self, filter_text):
        filter_pattern = QtCore.QRegExp(filter_text, Qt.CaseInsensitive, QtCore.QRegExp.FixedString)
        for index in range(self.window.task_list.count()):
            item = self.window.task_list.item(index)
            item_widget = self.window.task_list.itemWidget(item)
            line_edit = item_widget.findChild(QLineEdit, "task_text")
            if line_edit:
                item_text = line_edit.text()
                matches_filter = filter_text == '' or filter_pattern.indexIn(item_text) != -1
                item.setHidden(not matches_filter)

    def shot_search(self, filter_text):
        filter_pattern = QtCore.QRegExp(filter_text, Qt.CaseInsensitive, QtCore.QRegExp.FixedString)
        for index in range(self.window.shot_list.count()):
            item = self.window.shot_list.item(index)
            item_text = item.text()
            matches_filter = filter_text == '' or filter_pattern.indexIn(item_text) != -1
            item.setHidden(not matches_filter)

    def handle_item_clicked(self, item):
        # Reset background color for all items
        for index in range(self.window.task_list.count()):
            list_item = self.window.task_list.item(index)
            task_card_ui = self.window.task_list.itemWidget(list_item)
            frame = task_card_ui.findChild(QtWidgets.QFrame, "frame")
            frame.setStyleSheet("""
                    QFrame {
                        background-color: rgb(50, 50, 50);
                        border: none;
                    }
                """)

        # Set the background color to orange for the clicked item's frame
        task_card_ui = self.window.task_list.itemWidget(item)
        frame = task_card_ui.findChild(QtWidgets.QFrame, "frame")
        frame.setStyleSheet("""
                QFrame {
                    background-color: rgb(247, 147, 30);
                    border: none;
                }
            """)

    def create_shot(self):
        shot_text = self.window.add_shot_text.text()
        if shot_text:
            if not self.dm.is_shot_duplicate(shot_text):
                self.dm.create_shot(shot_text)
                self.window.add_shot_text.clear()
                self.load_shot_list()

                # Select the newly added shot in the list
                items = self.window.shot_list.findItems(shot_text, QtCore.Qt.MatchExactly)
                if items:
                    self.window.shot_list.setCurrentItem(items[0])
            else:
                QtWidgets.QMessageBox.warning(self, "Duplicate Shot", f"The shot '{shot_text}' already exists.",
                                              QtWidgets.QMessageBox.Ok)

    def load_shot_list(self):
        self.window.shot_list.clear()
        shot_list = self.dm.get_shot_list()
        for shot in shot_list:
            item_text = shot.text
            item = QtWidgets.QListWidgetItem(item_text)
            item.setData(Qt.UserRole, shot.id)  # Store the shot's ID as data
            self.window.shot_list.addItem(item)

    def get_associated_shot_id(self):
        selected_shot_item = self.window.shot_list.currentItem()
        if selected_shot_item:
            return selected_shot_item.data(Qt.UserRole)
        return None

    def create_task_card(self):
        text = self.window.task_input_text.text()
        selected_shot_item = self.window.shot_list.currentItem()

        if text and selected_shot_item:
            associated_shot_id = selected_shot_item.data(Qt.UserRole)  # Get the shot's ID directly from the item

            self.dm.create_task_card(text, associated_shot_id)
            self.window.task_input_text.clear()

            self.window.urgent_button.setChecked(False)
            self.urgent_button_clicked()

            self.load_task_cards()
            self.update_filter()

    def load_task_cards(self, filter_date=True):
        self.window.task_list.clear()
        #self.window.task_list.setSpacing(5)

        filter_shot_id = self.get_associated_shot_id()

        current_filter = self.dm.current_date_filter
        task_cards = self.dm.get_task_cards_date(filter_shot_id, current_filter)

        # Sort the task cards by index before adding them to the list
        sorted_task_cards = sorted(task_cards, key=lambda x: x.index)

        for task_card in sorted_task_cards:
            task_card_ui = self.load_item_widget()
            task_text = task_card_ui.findChild(QtWidgets.QLineEdit, "task_text")
            completed_button = task_card_ui.findChild(QtWidgets.QRadioButton, "completed_button")
            urgent_button = task_card_ui.findChild(QtWidgets.QPushButton, "urgent_button")

            task_text.setText(task_card.text)
            completed_button.setChecked(task_card.completed)
            urgent_button.setChecked(task_card.urgent)

            list_item = QtWidgets.QListWidgetItem(self.window.task_list)
            list_item.setSizeHint(task_card_ui.sizeHint())

            # Set the data here
            list_item.setData(QtCore.Qt.UserRole, task_card.id)
            list_item.setData(QtCore.Qt.UserRole + 1, task_card.urgent)

            # Change background color of urgent_button to red if task is urgent
            if task_card.urgent:
                urgent_button.setStyleSheet("background-color: red;")

            # Connect the buttons
            completed_button.clicked.connect(lambda checked=False, task_id=task_card.id: self.dm.toggle_completed(task_id))
            urgent_button.clicked.connect(lambda checked=False, task_id=task_card.id: self.dm.toggle_urgent(task_id))
            task_text.textChanged.connect(lambda text, task_id=task_card.id: self.task_text_changed_slot(text, task_id))

            # UpdateFilters
            completed_button.clicked.connect(self.handle_list_button_clicked)
            urgent_button.clicked.connect(self.handle_list_button_clicked)

            self.window.task_list.addItem(list_item)
            self.window.task_list.setItemWidget(list_item, task_card_ui)

    def task_text_changed_slot(self, new_text, task_id):
        self.dm.update_task_card_text(task_id, new_text)

    def handle_frame_click(self):
        self.update_task_card_indices()

    def update_task_card_indices(self):
        for index in range(self.window.task_list.count()):
            list_item = self.window.task_list.item(index)
            task_card_ui = self.window.task_list.itemWidget(list_item)

            # Get the text of the task card
            task_text = task_card_ui.findChild(QtWidgets.QLineEdit, "task_text").text()

            # Update the index of the task card in your data model
            self.dm.update_task_card_index(task_text, index)

    def handle_list_button_clicked(self):
        self.update_filter()

    def update_filter(self):
        self.update_task_card_indices()  # cheat to update

        selected_index = self.window.filter_combobox.currentIndex()

        if selected_index != -1:
            # Simulate refreshing the task cards based on the selected filter
            self.filter_combobox_changed(selected_index)

            # If the same filter is selected again, clear the selection to refresh
            self.window.filter_combobox.setCurrentIndex(-1)
            self.window.filter_combobox.setCurrentIndex(selected_index)

    def urgent_button_clicked(self):
        state = self.window.urgent_button.isChecked()
        self.dm.urgent_button_state = state
        if state:
            self.window.urgent_button.setStyleSheet("background-color: red;")
        else:
            self.window.urgent_button.setStyleSheet("background-color: "";")

    def update_current_shot(self, current_item):
        if current_item:
            selected_shot_name = current_item.text()
            self.dm.current_shot = selected_shot_name

    def setup_shortcuts(self):
        central = self.window.shot_list

        keypress_ctl_f = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+F"), central)
        keypress_ctl_f.activated.connect(self.handle_ctrlf_shortcut)

        keypress_1 = QtWidgets.QShortcut(QtGui.QKeySequence("1"), central)
        keypress_1.activated.connect(self.shortcut_filter_todo)

        keypress_2 = QtWidgets.QShortcut(QtGui.QKeySequence("2"), central)
        keypress_2.activated.connect(self.shortcut_filter_urgent)

        keypress_3 = QtWidgets.QShortcut(QtGui.QKeySequence("3"), central)
        keypress_3.activated.connect(self.shortcut_filter_completed)

        keypress_4 = QtWidgets.QShortcut(QtGui.QKeySequence("4"), central)
        keypress_4.activated.connect(self.shortcut_filter_all)

        backspace_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence(Qt.Key_Backspace), self)
        backspace_shortcut.activated.connect(self.handle_backspace_shortcut)

        keypress_n = QtWidgets.QShortcut(QtGui.QKeySequence("N"), central)
        keypress_n.activated.connect(self.handle_n_shortcut)

    def handle_backspace_shortcut(self):
        focused_widget = QtWidgets.QApplication.focusWidget()

        if focused_widget == self.window.shot_list:
            self.delete_selected_shot()
        elif focused_widget == self.window.task_list:
            self.delete_selected_task()

    def handle_ctrlf_shortcut(self):
        focused_widget = QtWidgets.QApplication.focusWidget()

        if focused_widget == self.window.shot_list:
            self.window.shot_search.setFocus()
        elif focused_widget == self.window.task_list:
            self.window.text_search.setFocus()

    def handle_n_shortcut(self):
        focused_widget = QtWidgets.QApplication.focusWidget()

        if focused_widget == self.window.shot_list:
            self.window.add_shot_text.setFocus()
        elif focused_widget == self.window.task_list:
            self.window.task_input_text.setFocus()

    def shortcut_filter_todo(self):
        self.window.filter_combobox.setCurrentIndex(0)

    def shortcut_filter_urgent(self):
        self.window.filter_combobox.setCurrentIndex(1)

    def shortcut_filter_completed(self):
        self.window.filter_combobox.setCurrentIndex(2)

    def shortcut_filter_all(self):
        self.window.filter_combobox.setCurrentIndex(3)

    def setup_context_menu(self):
        self.window.task_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.window.task_list.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, point):
        context_menu = QtWidgets.QMenu(self)
        delete_action = context_menu.addAction("Delete")
        delete_action.triggered.connect(self.delete_selected_task)
        context_menu.exec_(self.window.task_list.mapToGlobal(point))

    def delete_selected_task(self):
        selected_item = self.window.task_list.currentItem()
        if selected_item:
            task_card_id = selected_item.data(QtCore.Qt.UserRole)  # Retrieve data

            # Show a confirmation dialog
            confirmation = QMessageBox.question(
                self, "Delete Task", "Are you sure you want to delete this task?",
                QMessageBox.No | QMessageBox.Yes
            )

            if confirmation == QMessageBox.Yes:
                self.dm.delete_task_card(task_card_id)
                self.load_task_cards()

    def setup_shot_context_menu(self):
        self.window.shot_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.window.shot_list.customContextMenuRequested.connect(self.show_shot_context_menu)

    def show_shot_context_menu(self, point):
        context_menu = QtWidgets.QMenu(self)
        rename_shot_action = context_menu.addAction("Rename")
        delete_shot_action = context_menu.addAction("Delete")
        selected_item = self.window.shot_list.itemAt(point)
        if selected_item:
            delete_shot_action.triggered.connect(self.delete_selected_shot)
            rename_shot_action.triggered.connect(lambda: self.rename_selected_shot(selected_item))
            context_menu.exec_(self.window.shot_list.mapToGlobal(point))

    def rename_selected_shot(self, item):
        new_name, ok = QtWidgets.QInputDialog.getText(self, "Rename Shot", "Enter new name:",
                                                      QtWidgets.QLineEdit.Normal, item.text())
        if ok and new_name.strip():
            item.setText(new_name)

            # Update the data model
            shot_id = item.data(QtCore.Qt.UserRole)  # Retrieve data
            self.dm.update_shot_name(shot_id, new_name)

            # Update the current shot name if it's the currently selected shot
            self.dm.current_shot = new_name

    def delete_selected_shot(self):
        selected_item = self.window.shot_list.currentItem()
        if selected_item:
            shot_id = selected_item.data(QtCore.Qt.UserRole)

            # Show a confirmation dialog
            confirmation = QMessageBox.question(
                self, "Delete Shot", "Are you sure you want to delete this shot and its tasks?",
                QMessageBox.Yes | QMessageBox.No
            )

            if confirmation == QMessageBox.Yes:
                self.dm.delete_shot(shot_id)
                self.load_shot_list()
                self.load_task_cards()

    def closeEvent(self, event):
        self.handle_frame_click()  #Cheat to update
        self.dm.save_data_to_json()
        event.accept()


def open_panel():
    open_panel.window = MainWindow()
    open_panel.window.show()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()
