#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os
import random
import weakref

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

    def __init__(self, name):
        self.name = name
        self.list_table = list()

    def get_file(self, row):
        return self.list_table[row]

    def add_child(self, child):
        self.list_table.append(child)

    def remove_child(self, child):
        self.list_table.pop(child)

    def get_name(self):
        return self.name

    def count_row(self):
        return len(self.list_table)
    """
    def seach_index_table(self, index):
        for i in self.list_table:
            if i.index_table.row() == index.row() and i.index_table.column() == index.column():
                return i.index_table
        return None

    def seach_index_tree(self, index):
        for i in self.list_tree:
            if i.index_tree.row() == index.row() and i.index_tree.column() == index.column():
                return i.index_tree
        return None
    """
    """
    def index_check(self, index):
        if self.index_in_folder.row() == index.row() and self.index_in_folder.column() == index.column():
            return True
        else:
            return False
    """

class File():

    def __init__(self, source_index, folder):
        self.source_index = source_index
        self.folder = weakref.ref(folder)

    def get_folder(self):
        return self.folder()

class ProxyModel(QtCore.QAbstractProxyModel):

    def __init__(self):
        super().__init__()

    def init_tree(self, model):
        self.folder1 = Folder(">=0.5")
        self.folder2 = Folder("<0.5")

        rows = model.rowCount()
        column = model.columnCount()

        for i in range(column):
            for j in range(rows):
                index_table = QtCore.QPersistentModelIndex(model.index(j,i))

                if float(index_table.data(QtCore.Qt.DisplayRole)) >= 0.5:
                    self.folder1.add_child(File(index_table,self.folder1))
                else:
                    self.folder2.add_child(File(index_table,self.folder2))

    def data(self, proxyIndex, role):
        if role != QtCore.Qt.DisplayRole:
            return None
        
        if self.folder1.index_check(index):
            return self.folder1.get_name()
        if self.folder2.index_check(index):
            return self.folder2.get_name()
        
        index_in_folder = self.folder1.seach_index_table(index)

        if index_in_folder:
            return index_in_folder.data(QtCore.Qt.DisplayRole)
        else:
            index_in_folder = self.folder2.seach_index_table(index)
            return index_in_folder.data(QtCore.Qt.DisplayRole)

    def setSourceModel(self, model):
        self.init_tree(model)
        super().setSourceModel(model)

    def mapFromSource(self, index):
        if not index.isValid() or self.folder1.index_check(index) or self.folder2.index_check(index):
            return QtCore.QModelIndex()

        index_in_folder = self.folder1.seach_index_tree(index)

        if index_in_folder:
            return index_in_folder
        else:
            return self.folder2.seach_index_tree(index)

    def mapToSource(self, proxy_index):
        if not index.isValid() or self.folder1.index_check(index) or self.folder2.index_check(index):
            return QtCore.QModelIndex()

        index_in_folder = self.folder1.seach_index_table(index)

        if index_in_folder:
            return index_in_folder
        else:
            return self.folder2.seach_index_table(index)

    def rowCount(self, parent):
        if parent_index.isValid() and type(parent_index.internalPointer()) is Folder:
            folder = parent_index.internalPointer()
            return folder.count_row()
        else:
            return 2

    def index(self, row, column, parent_index):
        if parent_index.isValid() and type(parent_index.internalPointer()) is Folder:
            folder = parent_index.internalPointer()
            file = folder.get_file(row)
            return self.createIndex(row, column, file)
        else:
            if row == 0:
                return self.createIndex(row, column, self.folder1)
            else:
                return self.createIndex(row, column, self.folder2)

    def columnCount(self, parent):
        return 1

    def parent(self, child_index):
        if child_index.isValid() and type(child_index.internalPointer()) is File:
            file = child_index.internalPointer()
            folder = file.get_folder()
            if self.folder1 is folder:
                return self.createIndex(1, 0, self.folder1)
            else:
                return self.createIndex(2, 0, self.folder2)
        else:
            return QtCore.QModelIndex()


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