import logging
import os

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QMessageBox

from central_office import CentralOffice


class Ui_MainWindow(QMainWindow):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 598)
        MainWindow.setAutoFillBackground(False)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.SendButton = QtWidgets.QPushButton(self.centralwidget)
        self.SendButton.setGeometry(QtCore.QRect(620, 470, 111, 41))
        self.SendButton.setObjectName("SendButton")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(50, 20, 161, 21))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(14)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(310, 20, 161, 21))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(14)
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(560, 20, 161, 21))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(14)
        self.label_3.setFont(font)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.RequestButton = QtWidgets.QPushButton(self.centralwidget)
        self.RequestButton.setGeometry(QtCore.QRect(620, 530, 111, 41))
        self.RequestButton.setObjectName("RequestButton")
        self.RequestField = QtWidgets.QLineEdit(self.centralwidget)
        self.RequestField.setGeometry(QtCore.QRect(240, 530, 371, 41))
        self.RequestField.setAlignment(QtCore.Qt.AlignCenter)
        self.RequestField.setObjectName("RequestField")
        self.BranchList = QtWidgets.QTextBrowser(self.centralwidget)
        self.BranchList.setGeometry(QtCore.QRect(40, 50, 181, 331))
        self.BranchList.setObjectName("BranchList")
        self.FileList = QtWidgets.QTextBrowser(self.centralwidget)
        self.FileList.setGeometry(QtCore.QRect(300, 50, 181, 331))
        self.FileList.setObjectName("FileList")
        self.LogList = QtWidgets.QTextBrowser(self.centralwidget)
        self.LogList.setGeometry(QtCore.QRect(550, 50, 181, 331))
        self.LogList.setObjectName("LogList")
        self.RefreshFilesButton = QtWidgets.QPushButton(self.centralwidget)
        self.RefreshFilesButton.setGeometry(QtCore.QRect(300, 390, 181, 41))
        self.RefreshFilesButton.setObjectName("RefreshFilesButton")
        self.RefreshBranchesButton = QtWidgets.QPushButton(self.centralwidget)
        self.RefreshBranchesButton.setGeometry(QtCore.QRect(40, 390, 181, 41))
        self.RefreshBranchesButton.setObjectName("RefreshBranchesButton")
        self.RefreshLogsButton = QtWidgets.QPushButton(self.centralwidget)
        self.RefreshLogsButton.setGeometry(QtCore.QRect(550, 390, 181, 41))
        self.RefreshLogsButton.setObjectName("RefreshLogsButton")
        self.SendField = QtWidgets.QLineEdit(self.centralwidget)
        self.SendField.setGeometry(QtCore.QRect(240, 470, 371, 41))
        self.SendField.setAlignment(QtCore.Qt.AlignCenter)
        self.SendField.setObjectName("SendField")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.log_file = "central_office_logs.log"
        logging.basicConfig(filename=self.log_file, level=logging.DEBUG)

        self.central_office = CentralOffice()

        self.SendButton.clicked.connect(self._send_file)
        self.RequestButton.clicked.connect(self._request_file)
        self.RefreshLogsButton.clicked.connect(self._refresh_logs_field)
        self.RefreshFilesButton.clicked.connect(self._refresh_files_field)
        self.RefreshBranchesButton.clicked.connect(self._refresh_branches_field)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Центральный Офис"))
        self.SendButton.setText(_translate("MainWindow", "Отправить файл"))
        self.label.setText(_translate("MainWindow", "Список филиалов"))
        self.label_2.setText(_translate("MainWindow", "Список файлов"))
        self.label_3.setText(_translate("MainWindow", "История действий"))
        self.RequestButton.setText(_translate("MainWindow", "Запросить файл"))
        self.RequestField.setPlaceholderText(
            _translate(
                "MainWindow",
                "Введите название файла и идентификатор филиала через пробел.",
            )
        )
        self.BranchList.setPlaceholderText(
            _translate(
                "MainWindow",
                "Здесь будет отображаться список всех филиалов и их подключения.",
            )
        )
        self.FileList.setPlaceholderText(
            _translate(
                "MainWindow",
                "Здесь будет отображаться список всех файлов центрального офиса.",
            )
        )
        self.LogList.setPlaceholderText(
            _translate(
                "MainWindow",
                "Здесь будет отображаться история всех действий центрального офиса.",
            )
        )
        self.RefreshFilesButton.setText(
            _translate("MainWindow", "Обновить список файлов")
        )
        self.RefreshBranchesButton.setText(
            _translate("MainWindow", "Обновить список филиалов")
        )
        self.RefreshLogsButton.setText(
            _translate("MainWindow", "Обновить историю действий")
        )
        self.SendField.setPlaceholderText(
            _translate("MainWindow", "Введите идентификатор филиала для отправки.")
        )

    def __is_valid_branch_id(self, branch_id):
        error = QMessageBox()
        error.setWindowTitle("Ошибка")
        error.setIcon(QMessageBox.Warning)

        if not branch_id:
            error.setText("Введите идентификатор филиала.")
            error.exec_()
            return 0
        elif not branch_id.isnumeric():
            error.setText("Значение филиала должно быть числом из списка филиалов.")
            error.exec_()
            return 0
        elif branch_id not in self.central_office.branch_offices.keys():
            error.setText("Данный филиал не был найден в списке.")
            error.exec_()
            return 0

        return 1

    def _send_file(self):
        branch_id = self.SendField.text()

        if not self.__is_valid_branch_id(branch_id):
            return

        try:
            fname = QFileDialog.getOpenFileName(self)[0]
        except Exception as e:
            logging.error(f"Ошибка открытия файла.")
            return

        self.central_office.send_file(fname, branch_id)

    def _request_file(self):
        try:
            file_name, branch_id = self.RequestField.text().split(" ")
        except:
            error = QMessageBox()
            error.setWindowTitle("Ошибка")
            error.setIcon(QMessageBox.Warning)
            error.setText("Введите название файла и идентификатор филиала.")

            error.exec_()
            return

        if not self.__is_valid_branch_id(branch_id):
            return

        self.central_office.request_file(file_name, branch_id)

    def _refresh_branches_field(self):
        branches = self.central_office.branch_offices
        branches_to_show = ""

        for id, socket in branches.items():
            branches_to_show += f"Филиал №{id}: {socket} \n"
            branches_to_show += "\n"

        self.BranchList.setText(branches_to_show)

    def _refresh_files_field(self):
        directory_path = self.central_office.files_dir
        folder_info = {}
        files_to_show = ""

        for foldername, subfolders, filenames in os.walk(directory_path):
            folder_info[foldername] = filenames

        for foldername, filenames in folder_info.items():
            files_to_show += f"{foldername}: {', '.join(filenames)} \n"
            files_to_show += "\n"

        self.FileList.setText(files_to_show)

    def _refresh_logs_field(self):
        with open(self.log_file, "r") as file:
            data = file.read()

        self.LogList.setText(data)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
