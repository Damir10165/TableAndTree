#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QApplication, QWidget, QToolBar, QPushButton, QMainWindow, QAction, QTextEdit, QGridLayout, QTableView
from PyQt5 import QtSql

import sys

class Table(QTableView):

    def __init__(self):
        super().__init__()

        self.Table()

    def Table(self):
        self.con = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        self.con.setDatabaseName('db.sqlite')
        exec("")
        if self.con.open() != True:
            print(self.con.lastError().text())

        self.model = QtSql.QSqlTableModel(self)

        query = QtSql.QSqlQuery()

        #if query.exec("CREATE TABLE Persons (Person int, LastName varchar(255), FirstName varchar(255), Address varchar(255), City varchar(255));"):
        if query.exec("CREATE TABLE Numbers (f float);"):

            print("Create table is success")

            self.model.setTable('Numbers')
            self.model.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)

        query.clear()
        self.model.select()

        self.table = QTableView()
        self.table.setModel(self.model)

    def add_row(self):

        row_position = self.model.rowCount()
        column_position = self.model.columnCount()

        rec = self.con.record('Numbers')

        self.model.insertRow(row_position)
        self.model.select()

        print(rec.isEmpty())
        print(rec.count())

    def add_column(self):
        row_position = self.model.rowCount()
        column_position = self.model.columnCount()

        self.model.insertColumn(column_position)
        self.model.select()


class Window(QMainWindow):
    #главное окно

    def __init__(self):
        super().__init__()


        self.initUI()

    def initUI(self):


        #Таблица

        table = Table()

        #кнопки добавления строк и столбцов

        Action_1 = QAction('Добавить строку', self)
        Action_1.triggered.connect(table.add_row)

        Action_2 = QAction('Добавить столбец', self)
        Action_2.triggered.connect(table.add_column)

        self.toolbar = self.addToolBar('Добавить строку')
        self.toolbar.addAction(Action_1)

        self.toolbar = self.addToolBar('Добавить столбец')
        self.toolbar.addAction(Action_2)


        #таблица и дерево
        window = QWidget()

        Tree = QTextEdit()

        grid = QGridLayout()
        grid.setSpacing(5)

        grid.addWidget(table, 1, 0)
        grid.addWidget(Tree, 1, 1)

        window.setLayout(grid)

        self.setCentralWidget(window)

        self.setGeometry(500, 500, 500, 500)
        self.setWindowTitle("Главное окно")
        self.show()

if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Window()
    sys.exit(app.exec_())