#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QApplication, QWidget, QToolBar, QPushButton, QMainWindow, QAction,  QTableView, QTextEdit, QGridLayout
import sys


class Window(QMainWindow):
    #главное окно

    def __init__(self):
        super().__init__()


        self.initUI()

    def initUI(self):

        #кнопки добавления строк и столбцов

        Action_1 = QAction('Добавить строку', self)
        Action_2 = QAction('Добавить столбец', self)

        self.toolbar = self.addToolBar('Добавить строку')
        self.toolbar.addAction(Action_1)

        self.toolbar = self.addToolBar('Добавить столбец')
        self.toolbar.addAction(Action_2)


        #таблица и дерево
        Window = QWidget()

        Table = QTextEdit()
        Tree = QTextEdit()

        grid = QGridLayout()
        grid.setSpacing(5)

        grid.addWidget(Table, 1, 0)
        grid.addWidget(Tree, 1, 1)


        Window.setLayout(grid)

        self.setCentralWidget(Window)

        self.setGeometry(500, 500, 500, 500)
        self.setWindowTitle("Главное окно")
        self.show()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Window()
    sys.exit(app.exec_())