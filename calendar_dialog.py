from PySide2.QtGui import QPalette, QTextCharFormat
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QApplication, QCalendarWidget, QDialog, QVBoxLayout
from notes_model import TaskCardDataModel
import sys


class MyCalendarDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Date(s)")
        self.setModal(True)  # Make it a modal dialog
        self.dm = TaskCardDataModel()

        # Add the MyCalendar widget or any other content you need
        self.calendar_widget = MyCalendar()
        layout = QVBoxLayout()
        layout.addWidget(self.calendar_widget)
        self.setLayout(layout)

        self.selected_dates = []

    def closeEvent(self, event):
        self.update_calendar_dates()
        event.accept()

class MyCalendar(QCalendarWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.begin_date = None
        self.end_date = None

        self.highlight_format = QTextCharFormat()
        self.highlight_format.setBackground(self.palette().brush(QPalette.Highlight))
        self.highlight_format.setForeground(self.palette().color(QPalette.HighlightedText))

        self.clicked.connect(self.date_is_clicked)

    def format_range(self, format):
        if self.begin_date and self.end_date:
            d0 = min(self.begin_date, self.end_date)
            d1 = max(self.begin_date, self.end_date)
            while d0 <= d1:
                self.setDateTextFormat(d0, format)
                d0 = d0.addDays(1)

    def date_is_clicked(self, date):
        # reset highlighting of previously selected date range
        self.format_range(QTextCharFormat())
        if QApplication.keyboardModifiers() & Qt.ShiftModifier and self.begin_date:
            self.end_date = date
            # set highlighting of currently selected date range
            self.format_range(self.highlight_format)
        else:
            self.begin_date = date
            self.end_date = None

    def get_selected_dates(self):
        selected_dates = []
        if self.begin_date and self.end_date:
            d0 = min(self.begin_date, self.end_date)
            d1 = max(self.begin_date, self.end_date)
            while d0 <= d1:
                selected_dates.append(d0)
                d0 = d0.addDays(1)
        return selected_dates


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = MyCalendarDialog()
    dialog.exec_()
    sys.exit(app.exec_())
