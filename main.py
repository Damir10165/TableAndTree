#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (QApplication, QWidget, QToolBar, QPushButton,
                             QMainWindow, QAction, QTextEdit, QGridLayout,
                             QTableView)
from PyQt5 import QtSql


import sys
import os

class Connect(QtSql.QSqlDatabase):

    DATABASE_NAME = 'example.db'
    DATABASE_HOSTNAME = 'ExampleDataBase'

    def __init__(self):
        super().__init__()

        self.Connect_DataBase()

    def Connect_DataBase(self):
        if os.path.exists(self.DATABASE_NAME):
            self.Open_DataBase()
        else:
            self.Create_DataBase()

    def Open_DataBase(self):
        con = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        con.setHostName(self.DATABASE_HOSTNAME)
        con.setDatabaseName(self.DATABASE_NAME)

        if con.open():
            print("Open data base is success")
            return True
        else:
            print("Error open data base")
            return False

    def  Create_DataBase(self):
        if self.Open_DataBase():
           if self.Create_DataBase_Table():
               print("Create data base is success")
               return True
           else:
               print("Error create table")
               return False
        else:
            print("Error open data base for create table")
            return False

    def Create_DataBase_Table(self):

        query = QtSql.QSqlQuery()

        if query.exec("CREATE TABLE Numbers (f float)"):

            print("Create table is success")
            return True
        else:
            print("Error create table")
            return False

        query.clear()


class Table(QTableView):


    def __init__(self):
        super().__init__()

        self.con = Connect()

        self.Table()

    def Table(self):

        self.model = QtSql.QSqlTableModel(self, self.con)

        self.model.setTable('Numbers')
        self.model.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)

        self.model.select()

        self.table = QTableView()
        self.table.setModel(self.model)


    def add_row(self):

        row_position = self.model.rowCount()
        column_position = self.model.columnCount()

        #rec = self.con.record('Numbers')
        rec.setValue()

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

        self.table1 = Table()


        #кнопки добавления строк и столбцов

        Action_1 = QAction('Добавить строку', self)
        Action_1.triggered.connect(self.table1.add_row)

        Action_2 = QAction('Добавить столбец', self)
        Action_2.triggered.connect(self.table1.add_column)

        self.toolbar = self.addToolBar('Добавить строку')
        self.toolbar.addAction(Action_1)

        self.toolbar = self.addToolBar('Добавить столбец')
        self.toolbar.addAction(Action_2)


        #таблица и дерево
        window = QWidget()

        Tree = QTextEdit()

        grid = QGridLayout()
        grid.setSpacing(5)

        grid.addWidget(self.table1.table, 1, 0)
        grid.addWidget(Tree, 1, 1)

        window.setLayout(grid)

        self.setCentralWidget(window)


        self.setCentralWidget(window)
        self.setGeometry(500, 500, 500, 500)
        self.setWindowTitle("Главное окно")
        self.show()

if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Window()
    sys.exit(app.exec_())