import sys
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QFormLayout, QPushButton, QLineEdit, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QFileDialog, QSplitter, QDateEdit)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QPixmap, QImage
from PIL import Image
import database


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        #настройки окна
        self.setWindowTitle("Карта здоровья питомца")
        self.resize(1050, 650)
        self.setMinimumSize(850, 500)
        self.setStyleSheet("""
            QMainWindow { background-color: #f0f4f8; }""")
        self.setStyleSheet("""
            QMainWindow { background-color: #f0f4f8; }
            QPushButton {
                background-color: #4a90d9; color: white; border: none;
                padding: 8px 16px; border-radius: 6px; font-weight: bold;}
            QPushButton:hover { background-color: #357abd; }
            QTableWidget {
                background-color: white; alternate-background-color: #f9f9f9;
                gridline-color: #d0d7de;}
            QLineEdit, QDateEdit {
                padding: 6px; border: 1px solid #ccc; border-radius: 4px;}""")

        #подключение базы данных
        self.db = database.DatabaseManager()
        self.db.init_db()

        #создание интерфейса
        self._setup_ui()
        self._bind_signals()

        #загрузка данных
        self._refresh_table()
        self._current_image_path = ""

    #создание интерфейса
    def _setup_ui(self):
        #глав виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        #таблица
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Кличка", "Вид", "Прививка", "Дата", "Ветеринар", "Путь к фото"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setColumnHidden(6, True) #скрытие ID

        left_layout.addWidget(self.table)

        #кнопки под таблицей
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Добавить")
        self.btn_edit = QPushButton("Изменить")
        self.btn_delete = QPushButton("Удалить")
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        left_layout.addLayout(btn_layout)

        #форма заполнения информации
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)

        self.line_name = QLineEdit()
        self.line_species = QLineEdit()
        self.line_vaccine = QLineEdit()
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.line_vet = QLineEdit()

        form_layout.addRow("Кличка:", self.line_name)
        form_layout.addRow("Вид:", self.line_species)
        form_layout.addRow("Прививка:", self.line_vaccine)
        form_layout.addRow("Дата прививки:", self.date_edit)
        form_layout.addRow("Ветеринар:", self.line_vet)

        right_layout.addWidget(form_widget)

        #фото
        self.label_image = QLabel("Фото питомца")
        self.label_image.setAlignment(Qt.AlignCenter)
        self.label_image.setMinimumHeight(200)
        self.label_image.setStyleSheet("background-color: #f5f5f5; border: 2px dashed #bbb; border-radius: 8px;")
        right_layout.addWidget(self.label_image)

        #загрузка фото кнопка
        self.btn_load_image = QPushButton("Загрузить фото")
        right_layout.addWidget(self.btn_load_image)

        right_layout.addStretch()

        #разделитель
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([500, 350])

        main_layout.addWidget(splitter)

    #привязка сигналов
    def _bind_signals(self):
        self.btn_add.clicked.connect(self._on_add)
        self.btn_edit.clicked.connect(self._on_edit)
        self.btn_delete.clicked.connect(self._on_delete)
        self.btn_load_image.clicked.connect(self._on_load_image)
        self.table.itemSelectionChanged.connect(self._on_select_row)

    #добавление записи
    def _on_add(self):
        if not self.line_name.text().strip():
            QMessageBox.warning(self, "Ошибка", "Поле 'Кличка' обязательно!")
            return

        data = {
            "name": self.line_name.text().strip(),
            "species": self.line_species.text().strip(),
            "vaccine": self.line_vaccine.text().strip(),
            "date": self.date_edit.date().toString("yyyy-MM-dd"),
            "vet": self.line_vet.text().strip(),
            "image_path": self._current_image_path}

        self.db.insert_record(data)
        self._refresh_table()
        self._clear_fields()
        QMessageBox.information(self, "Успех", "Запись добавлена!")

    #редактирование записи
    def _on_edit(self):
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите запись в таблице.")
            return

        row = selected[0].row()
        item_id = self.table.item(row, 0).data(Qt.UserRole)

        data = {
            "id": item_id,
            "name": self.line_name.text().strip(),
            "species": self.line_species.text().strip(),
            "vaccine": self.line_vaccine.text().strip(),
            "date": self.date_edit.date().toString("yyyy-MM-dd"),
            "vet": self.line_vet.text().strip()}

        self.db.update_record(data)
        self._refresh_table()
        QMessageBox.information(self, "Успех", "Запись обновлена!")

    #удаление записи
    def _on_delete(self):
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите запись для удаления.")
            return

        reply = QMessageBox.question(
            self, "Подтверждение",
            "Удалить выбранную запись?",
            QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            row = selected[0].row()
            item_id = self.table.item(row, 0).data(Qt.UserRole)
            self.db.delete_record(item_id)
            self._refresh_table()
            self._clear_fields()

    #заполнение формы при выборе строки
    def _on_select_row(self):
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            self._clear_fields()
            return

        row = selected[0].row()
        self.line_name.setText(self.table.item(row, 1).text())
        self.line_species.setText(self.table.item(row, 2).text())
        self.line_vaccine.setText(self.table.item(row, 3).text())

        date_str = self.table.item(row, 4).text()
        if date_str:
            date = QDate.fromString(date_str, "yyyy-MM-dd")
            self.date_edit.setDate(date)

        self.line_vet.setText(self.table.item(row, 5).text())

        # загрузка фото
        image_path = self.table.item(row, 6).text() if self.table.columnCount() > 6 else ""
        if image_path and image_path.strip():
            try:
                from PIL import Image
                img = Image.open(image_path).convert("RGBA")
                img.thumbnail((250, 250), Image.LANCZOS)
                qt_img = QImage(img.tobytes(), img.width, img.height, QImage.Format_RGBA8888)
                pixmap = QPixmap.fromImage(qt_img)
                self.label_image.setPixmap(pixmap)
                self.label_image.setScaledContents(True)
                self.label_image.setStyleSheet("background-color: white; border: 2px solid #999; border-radius: 8px;")
                self._current_image_path = image_path
            except Exception as e:
                #если фото не загрузилось
                self.label_image.setText("Фото питомца")
                self.label_image.setStyleSheet(
                    "background-color: #f5f5f5; border: 2px dashed #bbb; border-radius: 8px;")
                self._current_image_path = ""
        else:
            self.label_image.setText("Фото питомца")
            self.label_image.setStyleSheet("background-color: #f5f5f5; border: 2px dashed #bbb; border-radius: 8px;")
            self._current_image_path = ""

    #загрузка и масштабирование фото
    def _on_load_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Выберите изображение", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif)")

        if not path:
            return

        try:
            img = Image.open(path).convert("RGBA")
            img.thumbnail((250, 250), Image.LANCZOS)

            qt_img = QImage(
                img.tobytes(), img.width, img.height,
                QImage.Format_RGBA8888)
            pixmap = QPixmap.fromImage(qt_img)
            self._current_image_path = path
            self.label_image.setPixmap(pixmap)
            self.label_image.setScaledContents(True)
            self.label_image.setStyleSheet(
                "background-color: white; border: 2px solid #999; border-radius: 8px;")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить изображение:\n{e}")

    #обновление таблицы
    def _refresh_table(self):
        self.table.setRowCount(0)
        records = self.db.get_all()

        for i, rec in enumerate(records):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(str(rec["id"])))
            self.table.setItem(i, 1, QTableWidgetItem(rec["name"]))
            self.table.setItem(i, 2, QTableWidgetItem(rec["species"] or ""))
            self.table.setItem(i, 3, QTableWidgetItem(rec["vaccine"] or ""))
            self.table.setItem(i, 4, QTableWidgetItem(rec["date"] or ""))
            self.table.setItem(i, 5, QTableWidgetItem(rec["vet"] or ""))
            self.table.setItem(i, 6, QTableWidgetItem(rec["image_path"] or ""))

            #сохранение ID в скрытой роли
            self.table.item(i, 0).setData(Qt.UserRole, rec["id"])

    #очистка полей формы
    def _clear_fields(self):
        self.line_name.clear()
        self.line_species.clear()
        self.line_vaccine.clear()
        self.date_edit.setDate(QDate.currentDate())
        self.line_vet.clear()
        self.label_image.setText("Фото питомца")
        self.label_image.setStyleSheet(
            "background-color: #f5f5f5; border: 2px dashed #bbb; border-radius: 8px;")
        self._current_image_path = ""

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self, "Выход",
            "Вы уверены, что хотите выйти?",
            QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.db.close()
            event.accept()
        else:
            event.ignore()