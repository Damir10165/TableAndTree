#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os
import random

from PyQt5.QtWidgets import (QApplication, QWidget, QToolBar, QPushButton,
                             QMainWindow, QAction, QTextEdit, QGridLayout,
                             QTableView, QDoubleSpinBox, QStyledItemDelegate)
from PyQt5 import QtSql
from PyQt5 import QtCore

DATABASE_NAME = 'example.db'

def connect_data_base():
    if os.path.exists(DATABASE_NAME):
        return open_data_base()
    else:
        return create_data_base()

def open_data_base():
    con = QtSql.QSqlDatabase.addDatabase('QSQLITE')
    con.setDatabaseName(DATABASE_NAME)

    if con.open():
        print("Open data base is success")
        return con
    else:
        print("Error open data base")
        return None

def create_data_base():
    con = open_data_base()
    if con is not None:
        if create_data_base_table(con):
            print("Create data base is success")
            return con
        else:
            print("Error create table")
            return None
    else:
        print("Error open data base for create table")
        return None

def create_data_base_table(con):
    if con.exec("CREATE TABLE Numbers (a float, b float, c float)"):

        print("Create table is success")
        return True
    else:
        print("Error create table")
        return None


class SpinBoxDelegate(QStyledItemDelegate):

    def createEditor(self, parent, option, index):

        editor = QDoubleSpinBox(parent)

        editor.setMinimum(0)
        editor.setMaximum(1)

        return editor

class Table(QTableView):

    def __init__(self):
        super().__init__()

        self.con = connect_data_base()

        self.model = QtSql.QSqlTableModel(self, self.con)
        self.model.setTable('Numbers')
        self.model.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
        self.model.select()
        self.setModel(self.model)

        delegate = SpinBoxDelegate()
        self.setItemDelegate(delegate)

    def add_row(self):
        # Добавление в каждый столбец нового элемента.
        rec = QtSql.QSqlRecord()
        rec.append(QtSql.QSqlField('a'))
        rec.append(QtSql.QSqlField('b'))
        rec.append(QtSql.QSqlField('c'))

        rec.setValue('a', float('{:.2}'.format(random.uniform(0,1))))
        rec.setValue('b', float('{:.2}'.format(random.uniform(0,1))))
        rec.setValue('c', float('{:.2}'.format(random.uniform(0,1))))

        self.model.insertRecord(-1, rec)


class Window(QMainWindow):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):

        #таблица
        self.table1 = Table()

        #кнопка добавления строк
        Action_1 = QAction('Добавить строку', self)
        Action_1.triggered.connect(self.table1.add_row)

        self.toolbar = self.addToolBar('Добавить строку')
        self.toolbar.addAction(Action_1)

        #таблица и дерево
        window = QWidget()

        Tree = QTextEdit()

        grid = QGridLayout()
        grid.setSpacing(5)

        grid.addWidget(self.table1, 1, 0)
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