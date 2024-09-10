import sys
import pickle
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QLineEdit, QListWidgetItem, QCheckBox, QSystemTrayIcon, QMenu, QAction, QLabel
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

class TodoApp(QWidget):
    def __init__(self):
        super().__init__()
        
        self.todo_file = 'todos.pkl'
        self.initUI()
        self.load_todos()
        self.init_tray_icon()

    def initUI(self):
        self.setWindowTitle('Todo App')
        self.setGeometry(100, 100, 400, 350)

        # Layout principale
        layout = QVBoxLayout()

        # Lista di todo
        self.todo_list = QListWidget()
        layout.addWidget(self.todo_list)

        # Layout per l'inserimento di nuovi todo
        input_layout = QHBoxLayout()
        self.todo_input = QLineEdit()
        self.add_button = QPushButton('Add')
        self.add_button.clicked.connect(self.add_todo)

        input_layout.addWidget(self.todo_input)
        input_layout.addWidget(self.add_button)

        layout.addLayout(input_layout)

        # Pulsante per eliminare i todo completati
        self.delete_button = QPushButton('Delete Completed')
        self.delete_button.clicked.connect(self.delete_completed_todos)
        layout.addWidget(self.delete_button)

        self.setLayout(layout)

    def init_tray_icon(self):
        # Icona per il system tray
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("todo_icon.png"))  # Puoi usare qualsiasi icona tu voglia

        # Menu del system tray
        tray_menu = QMenu(self)

        open_action = QAction("Open", self)
        open_action.triggered.connect(self.show)
        tray_menu.addAction(open_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(QApplication.instance().quit)
        tray_menu.addAction(exit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def add_todo(self):
        todo_text = self.todo_input.text()
        if todo_text:
            self.add_todo_item(todo_text)
            self.todo_input.clear()
            self.save_todos()

    def add_todo_item(self, todo_text, completed=False):
        item_widget = QWidget()
        item_layout = QHBoxLayout()

        checkbox = QCheckBox()
        checkbox.setChecked(completed)
        checkbox.stateChanged.connect(self.save_todos)

        label = QLabel(todo_text)
        if completed:
            label.setStyleSheet("text-decoration: line-through;")

        item_layout.addWidget(checkbox)
        item_layout.addWidget(label)

        item_widget.setLayout(item_layout)
        list_item = QListWidgetItem(self.todo_list)
        list_item.setSizeHint(item_widget.sizeHint())
        self.todo_list.setItemWidget(list_item, item_widget)

    def save_todos(self):
        todos = []
        for i in range(self.todo_list.count()):
            item_widget = self.todo_list.itemWidget(self.todo_list.item(i))
            checkbox = item_widget.layout().itemAt(0).widget()
            label = item_widget.layout().itemAt(1).widget()
            todos.append((label.text(), checkbox.isChecked()))

        with open(self.todo_file, 'wb') as f:
            pickle.dump(todos, f)

    def load_todos(self):
        try:
            with open(self.todo_file, 'rb') as f:
                todos = pickle.load(f)
                for todo_text, completed in todos:
                    self.add_todo_item(todo_text, completed)
        except FileNotFoundError:
            pass

    def delete_completed_todos(self):
        for i in range(self.todo_list.count() - 1, -1, -1):  # Itera in ordine inverso per evitare problemi con l'indice
            item_widget = self.todo_list.itemWidget(self.todo_list.item(i))
            checkbox = item_widget.layout().itemAt(0).widget()
            if checkbox.isChecked():
                self.todo_list.takeItem(i)
        self.save_todos()

    def closeEvent(self, event):
        # Minimizza l'app nella taskbar
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Todo App",
            "L'app è ancora in esecuzione nella taskbar.",
            QSystemTrayIcon.Information,
            2000
        )

if __name__ == '__main__':
    app = QApplication(sys.argv)
    todo_app = TodoApp()
    todo_app.show()
    sys.exit(app.exec_())
