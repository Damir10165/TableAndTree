#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os
import random
import weakref

from PyQt5.QtWidgets import (QApplication, QWidget, QToolBar, QPushButton,
                             QMainWindow, QAction, QTextEdit, QGridLayout,
                             QTableView, QDoubleSpinBox, QStyledItemDelegate,
                             QTreeView, QListView, QAbstractItemView)
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

    def get_file_by_index(self, index):
        for row, file in enumerate(self.list_table):
            if file.get_source_index == index:
                return i, row
        return None, None


class File():

    def __init__(self, source_index, folder):
        self.source_index = source_index
        self.folder = weakref.ref(folder)

    def get_folder(self):
        return self.folder()

    def get_source_index(self):
        return QtCore.QModelIndex(self.source_index)


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

    def data(self, proxy_index, role):
        #print("data")
        if not proxy_index.isValid():
            return None
        if role == QtCore.Qt.DisplayRole:
            if  type(proxy_index.internalPointer()) is File:
                file = proxy_index.internalPointer()
                source_index = file.get_source_index()
                return source_index.data(QtCore.Qt.DisplayRole)

            else:
                folder = proxy_index.internalPointer()
                return folder.get_name()
        else:
            return None

    def setSourceModel(self, model):
        self.init_tree(model)
        super().setSourceModel(model)

    def mapFromSource(self, source_index):
        #print("mapFromSource")
        file = None
        row = None
        if source_index.isValid():
            if float(source_index.data(QtCore.Qt.DisplayRole)) >=0.5:
                file, row = self.folder1.get_file_by_index(source_index)
            else:
                file, row = self.folder2.get_file_by_index(source_index)
        #print(file, row)
        if file is None:
            return QtCore.QModelIndex()
        else:
            return self.createIndex(row, 0, file)

    def setData(self, proxy_index, value, role):
        print("setData")
        if not proxy_index.isValid():
            return False

        if role == QtCore.Qt.DisplayRole:
            if type(proxy_index.internalPointer()) is File:
                file = proxy_index.internalPointer()
                source_model = self.sourceModel()
                source_model.setData(file.get_source_index(), value, role)
                return True
        else:
            return False

    def mapToSource(self, proxy_index):
        #print("mapToSource")
        if proxy_index.isValid() and type(proxy_index.internalPointer()) is File:
            file = proxy_index.internalPointer()
            return file.get_source_index()
        else:
            return QtCore.QModelIndex()

    def rowCount(self, parent_index):
        #print("rowCount")
        if parent_index.isValid() and type(parent_index.internalPointer()) is Folder:
            folder = parent_index.internalPointer()
            return folder.count_row()
        else:
            return 2

    def index(self, row, column, parent_index):
        #print("index")
        if parent_index.isValid() and type(parent_index.internalPointer()) is Folder:
            folder = parent_index.internalPointer()
            file = folder.get_file(row)
            return self.createIndex(row, column, file)
        else:
            if row == 0:
                return self.createIndex(row, column, self.folder1)
            else:
                return self.createIndex(row, column, self.folder2)

    def columnCount(self, parent_index):
        #print("columnCount")
        return 1

    def parent(self, child_index):
        #print("parent")
        if child_index.isValid() and type(child_index.internalPointer()) is File:
            file = child_index.internalPointer()
            folder = file.get_folder()
            if self.folder1 is folder:
                return self.createIndex(0, 0, self.folder1)
            else:
                return self.createIndex(1, 0, self.folder2)
        else:
            return QtCore.QModelIndex()

    def flags(self, proxy_index):
        #print("flags")
        if proxy_index.isValid() and type(proxy_index.internalPointer()) is File:
            return QtCore.Qt.ItemFlag.ItemIsEditable
        return QtCore.Qt.ItemIsEnabled

    def dataChanged(self, topLeft, bottomRight, roles):
        print("dataChanged")

class Tree(QTreeView):

    def __init__(self, table_model):
        super().__init__()

        model = ProxyModel()
        model.setSourceModel(table_model)
        self.setModel(model)
        self.setEditTriggers(QAbstractItemView.EditTrigger.AllEditTriggers)

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