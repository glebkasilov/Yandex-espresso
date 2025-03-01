import sys
import os
import sqlite3

from PyQt6 import uic
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTableWidgetItem,
    QDialog,
    QMessageBox,
    QHeaderView
)

from UI.main_ui import Ui_MainWindow
from UI.addEditCoffeeForm_ui import Ui_Dialog


class AddEditCoffeeForm(QDialog, Ui_Dialog):
    def __init__(self, conn, coffee_id=None):
        super().__init__()
        self.setupUi(self)

        self.conn = conn
        self.coffee_id = coffee_id
        if self.coffee_id:
            self.load_coffee_data()
        self.priceEdit.setPlaceholderText("Например: 999.99")
        self.volumeEdit.setPlaceholderText("Например: 250.0")
        self.saveButton.clicked.connect(self.save_data)
        self.cancelButton.clicked.connect(self.reject)

    def load_coffee_data(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM coffee WHERE id = ?", (self.coffee_id,))
        data = cursor.fetchone()
        if data:
            self.nameEdit.setText(data[1])
            self.roastCombo.setCurrentText(data[2])
            self.typeCombo.setCurrentText(data[3])
            self.tasteEdit.setPlainText(data[4])
            self.priceEdit.setText(str(data[5]))
            self.volumeEdit.setText(str(data[6]))

    def validate_input(self):
        errors = []
        if not self.nameEdit.text().strip():
            errors.append("Название обязательно для заполнения")
        try:
            float(self.priceEdit.text())
        except ValueError:
            errors.append("Некорректный формат цены")
        try:
            float(self.volumeEdit.text())
        except ValueError:
            errors.append("Некорректный формат объема")
        return errors

    def save_data(self):
        errors = self.validate_input()
        if errors:
            QMessageBox.critical(self, "Ошибка", "\n".join(errors))
            return
        data = {
            'name': self.nameEdit.text().strip(),
            'roast': self.roastCombo.currentText(),
            'type': self.typeCombo.currentText(),
            'taste': self.tasteEdit.toPlainText().strip(),
            'price': float(self.priceEdit.text()),
            'volume': float(self.volumeEdit.text())
        }
        cursor = self.conn.cursor()
        try:
            if self.coffee_id:
                cursor.execute("""UPDATE coffee SET
                    name = ?, roast_level = ?, type = ?,
                    taste_description = ?, price = ?, package_volume = ?
                    WHERE id = ?""",
                               (data['name'], data['roast'], data['type'],
                                data['taste'], data['price'], data['volume'], self.coffee_id))
            else:
                cursor.execute("""INSERT INTO coffee 
                    (name, roast_level, type, taste_description, price, package_volume)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                               (data['name'], data['roast'], data['type'],
                                data['taste'], data['price'], data['volume']))
            self.conn.commit()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка БД", str(e))
            self.conn.rollback()


class CoffeeApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.addButton.clicked.connect(self.add_coffee)
        self.editButton.clicked.connect(self.edit_coffee)

        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, 'data', 'coffee.sqlite')
        self.conn = sqlite3.connect(db_path)

        self.load_data()

    def load_data(self):
        if self.conn is None:
            raise Exception("Подключение к базе данных отсутствует")
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM coffee")
        data = cursor.fetchall()
        self.tableWidget.setRowCount(len(data))
        headers = ['ID', 'Название', 'Обжарка', 'Тип', 'Вкус', 'Цена', 'Объем']
        self.tableWidget.setColumnCount(len(headers))
        self.tableWidget.setHorizontalHeaderLabels(headers)
        for row_idx, row in enumerate(data):
            for col_idx, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.tableWidget.setItem(row_idx, col_idx, item)
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.horizontalHeader().setSectionResizeMode(
            4, QHeaderView.ResizeMode.Stretch)

    def get_selected_id(self):
        selected = self.tableWidget.selectedItems()
        if not selected:
            QMessageBox.warning(
                self, "Ошибка", "Выберите запись для редактирования")
            return None
        return int(selected[0].text())

    def add_coffee(self):
        dialog = AddEditCoffeeForm(self.conn)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()

    def edit_coffee(self):
        coffee_id = self.get_selected_id()
        if not coffee_id:
            return
        dialog = AddEditCoffeeForm(self.conn, coffee_id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()

    def closeEvent(self, event):
        self.conn.close()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CoffeeApp()
    window.show()
    sys.exit(app.exec())
