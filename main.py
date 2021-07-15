#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QApplication, QWidget, QToolBar, QPushButton, QMainWindow, QAction, QTextEdit, QGridLayout, QTableView
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
            Open_DataBase()
        else:
            Create_DataBase()

    def Open_DataBase(self):
        con = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        con.setHostName(self.DATABASE_HOSTNAME)
        con.setDatabaseName(self.DATABASE_NAME)

        if con.open():
            print("Open data base is success")
        else:
            print("Error open data base")

    def  Create_DataBase(self):
        if self.Open_DataBase():
           if Create_DataBase_Table():
               print("Create data base is success")
           else:
               print("Error create table")
        else:
            print("Error open data base for create table")

    def Create_DataBase_Table(self):

        query = QtSql.QSqlQuery()

        if query.exec("CREATE TABLE Numbers (f float)"):

            print("Create table is success")
        else:
            print("Error create table")

        query.clear()


class Table(QTableView):

    DATABASE_NAME = 'example.db'

    def __init__(self):
        super().__init__()

        self.Table()

    def Table(self):

        self.con = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        self.con.setDatabaseName('example.db')

        if self.con.open() != True:
            print(self.con.lastError().text())

        self.model = QtSql.QSqlTableModel(self, self.con)


        #убрать, есть Database
        query = QtSql.QSqlQuery()
        #if query.exec("CREATE TABLE Persons (Person int, LastName varchar(255), FirstName varchar(255), Address varchar(255), City varchar(255));"):
        if query.exec("CREATE TABLE Numbers (f float)"):

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

        table1 = Table()

        #кнопки добавления строк и столбцов
        Action_1 = QAction('Добавить строку', self)
        Action_1.triggered.connect(table1.add_row)

        Action_2 = QAction('Добавить столбец', self)
        Action_2.triggered.connect(table1.add_column)

        self.toolbar = self.addToolBar('Добавить строку')
        self.toolbar.addAction(Action_1)

        self.toolbar = self.addToolBar('Добавить столбец')
        self.toolbar.addAction(Action_2)

        #таблица и дерево
        window = QWidget()

        Tree = QTextEdit()

        grid = QGridLayout()
        grid.setSpacing(5)

        grid.addWidget(table1.table, 1, 0)
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