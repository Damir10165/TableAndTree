#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (QApplication, QWidget, QToolBar, QPushButton,
                             QMainWindow, QAction, QTextEdit, QGridLayout,
                             QTableView)
from PyQt5 import QtSql

import random


import sys
import os
DATABASE_NAME = 'example.db'

def Connect_DataBase():
    if os.path.exists(DATABASE_NAME):
        return Open_DataBase()
    else:
        return Create_DataBase()


def Open_DataBase():
    con = QtSql.QSqlDatabase.addDatabase('QSQLITE')
    con.setDatabaseName(DATABASE_NAME)

    if con.open():
        print("Open data base is success")
        return con
    else:
        print("Error open data base")
        return None


def Create_DataBase():
    con = Open_DataBase()
    if con is not None:
        if Create_DataBase_Table(con):
            print("Create data base is success")
            return con
        else:
            print("Error create table")
            return None
    else:
        print("Error open data base for create table")
        return None


def Create_DataBase_Table(con):
    if con.exec("CREATE TABLE Numbers (a float, b float, c float)"):

        print("Create table is success")
        return True
    else:
        print("Error create table")
        return None

class Table(QTableView):


    def __init__(self):
        super().__init__()

        self.con = Connect_DataBase()

        self.model = QtSql.QSqlTableModel(self, self.con)

        self.model.setTable('Numbers')
        self.model.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)

        self.model.select()

        self.table = QTableView()
        self.table.setModel(self.model)


    def add_row(self):

        column_position = self.model.columnCount()


        rec = QtSql.QSqlRecord()

        rec.append(QtSql.QSqlField('a'))
        rec.append(QtSql.QSqlField('b'))
        rec.append(QtSql.QSqlField('c'))

        rec.setValue('a', float(1.0))
        rec.setValue('b', float(1.0))
        rec.setValue('c', float(1.0))

        self.model.insertRecord(-1, rec)





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


        self.toolbar = self.addToolBar('Добавить строку')
        self.toolbar.addAction(Action_1)


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