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

#a = weakref.ref(None)

DATABASE_NAME = 'example0.db'

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

    def del_row(self):

        row = self.model.rowCount() - 1
        self.model.removeRows(row, 1)
        self.model.select()


class Folder():

    def __init__(self, name):
        self.name = name
        self.list_table = list()

    def get_file(self, row):
        #print("get_file")
        #print(row, self.count_row(), len(self.list_table))
        return self.list_table[row]

    def add_child(self, child):
        if child in self.list_table:
            return
        child.set_folder(self)
        self.list_table.append(child)

    def remove_child(self, child):
        print("remove_childe")
        child.set_folder(None)
        print(child in self.list_table)
        self.list_table.remove(child)

    def get_name(self):
        return self.name

    def count_row(self):
        return len(self.list_table)

    def get_file_by_index(self, index):
        for row, file in enumerate(self.list_table):
            if file.get_source_index() == index:
                return file, row
        return None, None


class File():

    def __init__(self, source_index, folder):
        self.source_index = source_index
        self.folder = weakref.ref(folder)

        if folder is None:
            self.folder = None
        else:
            self.folder = weakref.ref(folder)
            self.folder().add_child(self)


    def get_folder(self):
        if self.folder is None:
            return None
        else:
            return self.folder()

    def get_source_index(self):
        return QtCore.QModelIndex(self.source_index)

    def set_folder(self, folder):

        if self.folder is None:
            if folder is None:
                return
        elif self.folder() == folder:
            return

        if folder is None:
            self.folder = None
        else:
            self.folder = weakref.ref(folder)
            self.folder().add_child(self)

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
                    File(index_table,self.folder1)
                else:
                    File(index_table,self.folder2)

    def data(self, proxy_index, role):
        #print("data")
        if not proxy_index.isValid():
            return None

        if  type(proxy_index.internalPointer()) is File:
            file = proxy_index.internalPointer()
            source_index = file.get_source_index()
            return source_index.data(role)

        else:
            if role == QtCore.Qt.DisplayRole:
                folder = proxy_index.internalPointer()
                return folder.get_name()
            else:
                return None

    def setSourceModel(self, model):
        #print("setSourceModel")
        self.init_tree(model)
        super().setSourceModel(model)
        model.dataChanged.connect(self.update_tree)
        #model.rowsInserted.connect(self.update_add_row)

    def mapFromSource(self, source_index):
        #print("mapFromSource")
        if not source_index.isValid():
            return QtCore.QModelIndex()
        file = None
        row = None
        #if type(source_index.internalPointer()) is File:
        if float(source_index.data(QtCore.Qt.DisplayRole)) >=0.5:
            file, row = self.folder1.get_file_by_index(source_index)
        else:
            file, row = self.folder2.get_file_by_index(source_index)

        if file is None:
            return QtCore.QModelIndex()
        else:
            return self.createIndex(row, 0, file)

    def setData(self, proxy_index, value, role):
        print("setData", role, value)
        if not proxy_index.isValid():
            return False

        if type(proxy_index.internalPointer()) is File:
            file = proxy_index.internalPointer()
            #print(file)
            source_model = self.sourceModel()
            source_model.setData(file.get_source_index(), value, role) #error
            return True
        else:
            return False

    def mapToSource(self, proxy_index):
        #print("mapToSource")
        if not proxy_index.isValid():
            return QtCore.QModelIndex()
        if type(proxy_index.internalPointer()) is File:
            file = proxy_index.internalPointer()
            return file.get_source_index()
        else:
            return QtCore.QModelIndex()

    def rowCount(self, parent_index):
        #print("rowCount")
        if not parent_index.isValid():
            return 2
        # ?
        if type(parent_index.internalPointer()) is Folder:
            folder = parent_index.internalPointer()
            return folder.count_row()
        else:
            #print("rowCount_else")
            return 0

    def index(self, row, column, parent_index):
        #print("index", row)
        if not parent_index.isValid():
            if row == 0:
                return self.createIndex(row, column, self.folder1)
            else:
                return self.createIndex(row, column, self.folder2)

        if type(parent_index.internalPointer()) is Folder:
            folder = parent_index.internalPointer()
            file = folder.get_file(row)
            return self.createIndex(row, column, file)
        else:
            return QtCore.QModelIndex()

    def columnCount(self, parent_index):
        #print("columnCount")
        return 1

    def parent(self, child_index):
        #print("parent")
        if not child_index.isValid():
            return QtCore.QModelIndex()

        if type(child_index.internalPointer()) is File:
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
        if not proxy_index.isValid():
            return QtCore.Qt.ItemFlag.NoItemFlags

        if type(proxy_index.internalPointer()) is File:
            return QtCore.Qt.ItemFlag.ItemIsEditable | QtCore.Qt.ItemFlag.ItemIsEnabled\
                   | QtCore.Qt.ItemFlag.ItemIsSelectable
        return QtCore.Qt.ItemFlag.ItemIsEnabled

    def update_tree(self, topLeft, bottomRight, roles):
        print("update_tree")
        if roles and not QtCore.Qt.DisplayRole in roles:
            return None

        row_begin = topLeft.row()
        row_end = bottomRight.row()

        column_begin = topLeft.column()
        column_end = bottomRight.column()

        print(row_begin, row_end)
        print(column_begin, column_end)

        array_source_index = list()

        for i in range(row_begin, row_end+1):
            for j in range(column_begin, column_end+1):

                source_index = self.sourceModel().index(i, j)
                file, row = self.folder1.get_file_by_index(source_index)

                if file is not None and row is not None:
                    #переместить if так, чтобы проверка на пустату данных выполнялась в самом крайнем случае(в конце if)
                    if source_index.data(QtCore.Qt.DisplayRole) is None:
                        print("del_folder1")
                        folder1_index = self.createIndex(0, 0, self.folder1)
                        self.beginRemoveRows(folder1_index, row, row)
                        self.folder1.remove_child(file)
                        self.endRemoveRows()

                        continue

                    proxy_index = self.createIndex(row, 0, file)

                    if source_index.data(QtCore.Qt.DisplayRole) >= 0.5:
                        self.dataChanged.emit(proxy_index, proxy_index, [QtCore.Qt.DisplayRole])
                    else:
                        array_source_index.append(source_index)
                else:

                    file, row = self.folder2.get_file_by_index(source_index)

                    if file is not None and row is not None:

                        if source_index.data(QtCore.Qt.DisplayRole) is None:
                            print("del_folder2")
                            folder2_idnex = self.createIndex(1, 0, self.folder2)
                            self.beginRemoveRows(folder2_idnex, row, row)
                            self.folder2.remove_child(file)
                            self.endRemoveRows()

                            continue

                        proxy_index = self.createIndex(row, 0, file)

                        if source_index.data(QtCore.Qt.DisplayRole) < 0.5:
                            self.dataChanged.emit(proxy_index, proxy_index, [QtCore.Qt.DisplayRole])
                        else:
                            array_source_index.append(source_index)
                    else:

                        if source_index.data(QtCore.Qt.DisplayRole) >= 0.5:

                            folder1_index = self.createIndex(0, 0, self.folder1)

                            row = self.folder1.count_row()

                            self.beginInsertRows(folder1_index, row, row)
                            File(source_index, self.folder1)
                            self.endInsertRows()

                        else:

                            folder2_idnex = self.createIndex(1, 0, self.folder2)

                            row = self.folder2.count_row()

                            self.beginInsertRows(folder2_idnex, row, row)
                            File(source_index, self.folder2)
                            self.endInsertRows()

        for source_index in array_source_index:

            file, row = self.folder1.get_file_by_index(source_index)

            if file is not None and row is not None:

                print("folder_del_and_add")

                folder1_index = self.createIndex(0, 0, self.folder1)

                self.beginRemoveRows(folder1_index, row, row) #error
                self.folder1.remove_child(file)
                self.endRemoveRows()

                folder2_idnex = self.createIndex(1, 0, self.folder2)

                new_row = self.folder2.count_row()
                self.beginInsertRows(folder2_idnex, new_row,new_row)
                file.set_folder(self.folder2)
                self.endInsertRows()

            else:
                print("folder_del_and_add_2")
                file, row = self.folder2.get_file_by_index(source_index)

                folder2_idnex = self.createIndex(1, 0, self.folder2)

                self.beginRemoveRows(folder2_idnex, row, row)
                self.folder2.remove_child(file)
                self.endRemoveRows()

                folder1_index = self.createIndex(0, 0, self.folder1)

                new_row = self.folder1.count_row()
                self.beginInsertRows(folder1_index, new_row,new_row)
                file.set_folder(self.folder1)
                self.endInsertRows()

    def update_add_row(self, parent, first, last):
        print("update_add_row")

        for i in range(first, last+1):
            for j in range(3):
                source_index = QtCore.QPersistentModelIndex(self.sourceModel().index(i, j))

                if source_index.data(QtCore.Qt.DisplayRole) >= 0.5:

                    folder1_index = self.createIndex(0, 0, self.folder1)

                    file = File(source_index, self.folder1)
                    row = self.folder1.count_row()

                    self.beginInsertRows(folder1_index, row, row)
                    file.set_folder(self.folder1)
                    self.endInsertRows()

                else:

                    folder2_idnex = self.createIndex(1, 0, self.folder2)

                    file = File(source_index, self.folder2)
                    row = self.folder2.count_row()

                    self.beginInsertRows(folder2_idnex, row, row)
                    file.set_folder(self.folder2)
                    self.endInsertRows()


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

        #таблица и дерево
        self.table1 = Table()
        self.tree = Tree(self.table1.model)

        #кнопка добавления строк
        Action_1 = QAction('Добавить строку', self)
        Action_1.triggered.connect(self.table1.add_row)
        self.toolbar = self.addToolBar('Добавить строку')
        self.toolbar.addAction(Action_1)

        Action_2 = QAction('Удалить строку', self)
        Action_2.triggered.connect(self.table1.del_row)
        self.toolbar = self.addToolBar('Удалить строку')
        self.toolbar.addAction(Action_2)

        window = QWidget()

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