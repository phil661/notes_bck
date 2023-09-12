import sys
from PySide2.QtWidgets import QApplication, QDialog, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QCheckBox, QPushButton


class FilterDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Checkbox Dialog")

        # Create a layout for the dialog
        layout = QVBoxLayout(self)

        # Create a QTreeWidget for the dropdown
        dropdown_tree = QTreeWidget(self)
        dropdown_tree.setHeaderHidden(True)
        layout.addWidget(dropdown_tree)

        # Create the first section in the dropdown
        section1 = QTreeWidgetItem(dropdown_tree)
        section1.setText(0, "Status")
        section1.setExpanded(True)

        for item_text in ["To Do", "Completed", "Urgent"]:
            item = QTreeWidgetItem(section1)
            checkbox = QCheckBox(self)
            checkbox.setText(item_text)
            dropdown_tree.setItemWidget(item, 0, checkbox)

        # Create the second section in the dropdown
        section2 = QTreeWidgetItem(dropdown_tree)
        section2.setText(0, "Date Created")
        section2.setExpanded(True)

        for item_text in ["Today", "Yesterday", "Last Week"]:
            item = QTreeWidgetItem(section2)
            checkbox = QCheckBox(self)
            checkbox.setText(item_text)
            dropdown_tree.setItemWidget(item, 0, checkbox)

        # Create a "Clear All" button
        clear_button = QPushButton("Clear All", self)
        clear_button.clicked.connect(self.clearCheckboxes)
        layout.addWidget(clear_button)

    def clearCheckboxes(self):
        # Iterate through all items in the QTreeWidget and uncheck checkboxes
        for item in self.findChildren(QCheckBox):
            item.setChecked(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = FilterDialog()
    dialog.exec_()
    sys.exit(app.exec_())
