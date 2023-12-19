import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QMessageBox, QDialog, QComboBox
import psycopg2

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Администраторская панель")
        self.setGeometry(100, 100, 400, 300)

        # Создание главного виджета для размещения всех элементов
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)

        # Создание вертикального компоновщика для размещения элементов в главном виджете
        layout = QVBoxLayout(main_widget)

        # QLabel с инструкциями
        label = QLabel("Выберите проект:")
        layout.addWidget(label)

        # QComboBox для отображения доступных проектов из базы данных
        self.project_combobox = QComboBox()
        layout.addWidget(self.project_combobox)

        # QLabel для отображения текущего описания проекта
        self.description_label = QLabel()
        layout.addWidget(self.description_label)

        # QLabel для отображения текущего статуса проекта
        self.status_label = QLabel()
        layout.addWidget(self.status_label)

        # Кнопки для обновления описания и статуса
        update_description_button = QPushButton("Обновить описание")
        layout.addWidget(update_description_button)

        update_status_button = QPushButton("Обновить статус")
        layout.addWidget(update_status_button)

        delete_project_button = QPushButton('Удалить проект')
        layout.addWidget(delete_project_button)

        # Подключение сигнала нажатия кнопок обновления описания и статуса к соответствующим методам
        update_description_button.clicked.connect(self.update_description)
        update_status_button.clicked.connect(self.update_status)
        delete_project_button.clicked.connect(self.update_projects)

        # Получение списка проектов из базы данных
        self.load_projects()

    def load_projects(self):
        try:
            conn = psycopg2.connect(
                host="localhost",
                database="postgres",
                user="postgres",
                password="postgres"
            )
            cursor = conn.cursor()

            # Выполнение запроса на получение списка проектов
            cursor.execute("SELECT title FROM projects")
            projects = [row[0] for row in cursor.fetchall()]

            # Очистка QComboBox и заполнение его полученными проектами
            self.project_combobox.clear()
            self.project_combobox.addItems(projects)

            cursor.close()
            conn.close()

        except (Exception, psycopg2.Error) as error:
            print("Ошибка при получении списка проектов:", error)

    def del_projects(self,project_name,dialog):
        try:
            conn = psycopg2.connect(
                host="localhost",
                database="postgres",
                user="postgres",
                password="postgres"
            )
            cursor = conn.cursor()

            # Выполнение запроса на обновление описания проекта
            cursor.execute(f"DELETE FROM projects where title = '{project_name}'")
            conn.commit()

            cursor.close()
            conn.close()



            dialog.close()

        except (Exception, psycopg2.Error) as error:
            QMessageBox.warning(self, "Ошибка", "Ошибка при обновлении описания проекта: {}".format(error))
    def update_projects(self):
        project_name = self.project_combobox.currentText()

        dialog = QDialog(self)
        dialog.setWindowTitle("Удалить проект")

        label = QLabel("Имя проекта:")
        description_input = QLineEdit()

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(description_input)

        save_button = QPushButton("Удалить")
        save_button.clicked.connect(lambda: self.del_projects(project_name,dialog))
        layout.addWidget(save_button)

        dialog.setLayout(layout)
        dialog.exec()
    def update_description(self):
        project_name = self.project_combobox.currentText()

        dialog = QDialog(self)
        dialog.setWindowTitle("Обновить описание")

        label = QLabel("Описание проекта:")
        description_input = QLineEdit()

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(description_input)

        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(lambda: self.save_description(project_name, description_input.text(), dialog))
        layout.addWidget(save_button)

        dialog.setLayout(layout)
        dialog.exec()

    def save_description(self, project_name, description, dialog):
        try:
            conn = psycopg2.connect(
                host="localhost",
                database="postgres",
                user="postgres",
                password="postgres"
            )
            cursor = conn.cursor()

            # Выполнение запроса на обновление описания проекта
            cursor.execute("UPDATE projects SET description = %s WHERE title = %s", (description, project_name))
            conn.commit()

            cursor.close()
            conn.close()

            # Обновление текущего описания проекта
            self.load_project_details(project_name)

            dialog.close()

        except (Exception, psycopg2.Error) as error:
            QMessageBox.warning(self, "Ошибка", "Ошибка при обновлении описания проекта: {}".format(error))

    def update_status(self):
        project_name = self.project_combobox.currentText()

        dialog = QDialog(self)
        dialog.setWindowTitle("Обновить статус")

        label = QLabel("Статус проекта:")
        status_input = QLineEdit()

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(status_input)

        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(lambda: self.save_status(project_name, status_input.text(), dialog))
        layout.addWidget(save_button)

        dialog.setLayout(layout)
        dialog.exec()



    def save_status(self, project_name, status, dialog):
        try:
            conn = psycopg2.connect(
                host="localhost",
                database="postgres",
                user="postgres",
                password="postgres"
            )
            cursor = conn.cursor()

            # Выполнение запроса на обновление статуса проекта
            cursor.execute("UPDATE projects SET id_status = %s WHERE title = %s", (status, project_name))
            conn.commit()

            cursor.close()
            conn.close()

            # Обновление текущего статуса проекта
            self.load_project_details(project_name)

            dialog.close()

        except (Exception, psycopg2.Error) as error:
            QMessageBox.warning(self, "Ошибка", "Ошибка при обновлении статуса проекта: {}".format(error))

    def load_project_details(self, project_name):
        try:
            conn = psycopg2.connect(
                host="localhost",
                database="postgres",
                user="postgres",
                password="postgres"
            )
            cursor = conn.cursor()

            # Получение данных проекта из базы данных
            cursor.execute("SELECT description, id_status FROM projects WHERE title = %s", (project_name,))
            result = cursor.fetchone()

            if result:
                description, status = result
                self.description_label.setText("Описание: {}".format(description))
                self.status_label.setText("Статус: {}".format(status))
            else:
                self.description_label.setText("Описание: -")
                self.status_label.setText("Статус: -")

            cursor.close()
            conn.close()

        except (Exception, psycopg2.Error) as error:
            print("Ошибка при получении данных проекта:", error)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())