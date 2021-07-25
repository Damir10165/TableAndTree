#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os
import random

from PyQt5.QtWidgets import (QApplication, QWidget, QToolBar, QPushButton,
                             QMainWindow, QAction, QTextEdit, QGridLayout,
                             QTableView, QDoubleSpinBox, QStyledItemDelegate,
                             QTreeView, QListView)
from PyQt5 import QtSql, QtCore, QtGui

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

    def __init__(self):
        super().__init__()

        # создание анимации перехода от синего к красному
        self.color = QtCore.QVariantAnimation()
        self.color.setStartValue(QtGui.QColor("blue"))
        self.color.setEndValue(QtGui.QColor("red"))

    def createEditor(self, parent, option, index):

        editor = QDoubleSpinBox(parent)

        #минимально и максимально допустимое значение в ячейке
        editor.setMinimum(0)
        editor.setMaximum(1)

        return editor

    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)

        #выбор цвета в зависимости от значения в ячейке
        option.backgroundBrush = self.color.interpolated(QtGui.QColor("blue"), QtGui.QColor("red"), index.data())


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

        rec.setValue('a', round(random.uniform(0,1), 2))
        rec.setValue('b', round(random.uniform(0,1), 2))
        rec.setValue('c', round(random.uniform(0,1), 2))

        self.model.insertRecord(-1, rec)


class TreeItem():

    def __init__(self, parent, data):

        self.parentItem = parent
        self.parentData = data


class Folder():

    def __init__(self, name, index_folder):
        self.name = name
        self.list_table = list()
        self.index_folder = index_folder

    def add_child(self, child):
        self.list_table.append(child)

    def remove_child(self, child):
        self.list_table.pop(child)

    def insert_child(self, child):
        self.list_table.insert(child.index_tree, child)

    def get_name(self):
        return self.name

    def count_row(self):
        return len(self.list_table)

    def seach_index_table(self, index):
        return self.list_table.index(index)

    def seach_index_tree(self, index):
        return self.list_tree.index(index)

    def get_index(self):
        return self.index_folder

class File():

    def __init__(self, index_table, index_tree):
        self.index_table = index_table
        self.index_tree = index_tree


class ProxyModel(QtCore.QAbstractProxyModel):

    def __init__(self):
        super().__init__()

    def init_tree(self, model):

        index_folder1 = QtCore.QPersistentModelIndex(self.createIndex(0, 0))
        index_folder2 = QtCore.QPersistentModelIndex(self.createIndex(1, 0))

        self.folder1 = Folder(">=0.5", index_folder1)
        self.folder2 = Folder("<0.5", index_folder2)

        rows = model.rowCount()
        column = model.columnCount()
        row1 = 0
        row2 = 0

        for i in range(column):
            for j in range(rows):
                index_table = QtCore.QPersistentModelIndex(model.index(j,i))

                if float(index_table.data(QtCore.Qt.DisplayRole)) >= 0.5:
                    index_tree = QtCore.QPersistentModelIndex(self.index(row1, 0, self.folder1))
                    self.folder1.add_child(File(index_table, index_tree))
                    row1 += 1
                else:
                    index_tree = QtCore.QPersistentModelIndex(self.index(row2, 0, self.folder2))
                    self.folder2.add_child(File(index_table, index_tree))
                    row2 += 1

    def data(self, proxyIndex, role):

        if role != QtCore.Qt.DisplayRole:
            return None
        else:
            return proxyIndex.data()

    def setSourceModel(self, model):
        self.init_tree(model)
        super().setSourceModel(model)

    def mapFromSource(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        index_folder = self.folder1.seach_index_tree(index)

        if index_folder:
            return index_folder
        else:
            return self.folder2.seach_index_tree(index)

    def mapToSource(self, index):
        if not index.isValid() or index == self.folder1.get_index() or index == self.folder2.get_index():
            return QtCore.QModelIndex()

        index_folder = self.folder1.seach_index_table(index)

        if index_folder:
            return index_folder
        else:
            return self.folder2.seach_index_table(index)

    def rowCount(self, parent):
        return self.folder1.count_row() + self.folder2.count_row()

    def index(self, row, column, folder):
        return self.createIndex(row, column, folder)

    def columnCount(self, parent):
        return 1

    def parent(self, index):
        if not index.isValid() or index == self.folder1.get_index() or index == self.folder2.get_index():
            return QtCore.QModelIndex()

        if self.folder1.seach_index_tree(index):
            return self.folder1.get_index()
        if self.folder2.seach_index_tree(index):
            return self.folder2.get_index()



class Tree(QTreeView):

    def __init__(self, table_model):
        super().__init__()

        model = ProxyModel()
        model.setSourceModel(table_model)
        self.setModel(model)


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

        self.tree = Tree(self.table1.model)

        grid = QGridLayout()
        grid.setSpacing(5)

        grid.addWidget(self.table1, 1, 0)
        grid.addWidget(self.tree, 1, 1)

        window.setLayout(grid)

        self.setCentralWidget(window)

        self.setCentralWidget(window)
        self.setGeometry(500, 500, 660, 500)
        self.setWindowTitle("Главное окно")
        self.show()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Window()
    sys.exit(app.exec_())