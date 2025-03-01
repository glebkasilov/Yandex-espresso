import sys
import sqlite3
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem


class CoffeeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.conn = sqlite3.connect('coffee.sqlite')
        self.load_data()

    def load_data(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM coffee")
        data = cursor.fetchall()
        self.tableWidget.setRowCount(len(data))
        self.tableWidget.setColumnCount(7)
        headers = [
            'ID', 'Название', 'Степень обжарки',
            'Тип', 'Описание вкуса', 'Цена', 'Объем упаковки'
        ]
        self.tableWidget.setHorizontalHeaderLabels(headers)
        for row_idx, row in enumerate(data):
            for col_idx, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.tableWidget.setItem(row_idx, col_idx, item)
        self.tableWidget.resizeColumnsToContents()

    def closeEvent(self, event):
        self.conn.close()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CoffeeApp()
    window.show()
    sys.exit(app.exec())
