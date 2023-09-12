import sys
from PySide2.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton
from PySide2.QtCore import QRect, QPropertyAnimation, QEasingCurve

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set window properties
        self.setWindowTitle("Main Window with Right Side Panel")
        self.setGeometry(100, 100, 800, 600)

        # Create central widget and main layout
        central_widget = QWidget()
        central_layout = QVBoxLayout(central_widget)

        # Create a button to toggle the side panel
        side_panel_button = QPushButton("Toggle Side Panel")
        side_panel_button.clicked.connect(self.toggle_side_panel)

        # Create the side panel widget
        self.side_panel = QWidget()
        self.side_panel.setFixedWidth(300)  # Set the width of the side panel
        self.side_panel_hidden = True

        # Add widgets to the layouts
        central_layout.addWidget(side_panel_button)

        # Set the central widget for the main window
        self.setCentralWidget(central_widget)

        # Initialize animation
        self.side_panel_animation = QPropertyAnimation(self.side_panel, b"geometry")
        self.side_panel_animation.setDuration(300)  # Animation duration in milliseconds
        self.side_panel_animation.setEasingCurve(QEasingCurve.OutQuint)

    def toggle_side_panel(self):
        if self.side_panel_hidden:
            # Animate the side panel sliding in from the right
            start_geometry = QRect(self.width(), 0, 0, self.height())
            end_geometry = QRect(self.width() - self.side_panel.width(), 0, self.side_panel.width(), self.height())

            self.side_panel_animation.setStartValue(start_geometry)
            self.side_panel_animation.setEndValue(end_geometry)
            self.side_panel.show()
            self.side_panel_animation.start()
        else:
            # Animate the side panel sliding out to the right
            start_geometry = QRect(self.width() - self.side_panel.width(), 0, self.side_panel.width(), self.height())
            end_geometry = QRect(self.width(), 0, 0, self.height())

            self.side_panel_animation.setStartValue(start_geometry)
            self.side_panel_animation.setEndValue(end_geometry)
            self.side_panel_animation.finished.connect(self.side_panel.hide)
            self.side_panel_animation.start()

        self.side_panel_hidden = not self.side_panel_hidden

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
