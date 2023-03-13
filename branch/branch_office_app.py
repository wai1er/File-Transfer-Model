import logging
import os

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QMessageBox

from branch_office import BranchOffice


class Ui_MainWindow(QMainWindow):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 598)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.SendButton = QtWidgets.QPushButton(self.centralwidget)
        self.SendButton.setGeometry(QtCore.QRect(50, 500, 181, 41))
        self.SendButton.setObjectName("SendButton")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(60, 20, 161, 21))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(14)
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(440, 20, 161, 21))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(14)
        self.label_3.setFont(font)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.RequestButton = QtWidgets.QPushButton(self.centralwidget)
        self.RequestButton.setGeometry(QtCore.QRect(620, 500, 111, 41))
        self.RequestButton.setObjectName("RequestButton")
        self.RequestField = QtWidgets.QLineEdit(self.centralwidget)
        self.RequestField.setGeometry(QtCore.QRect(300, 500, 301, 41))
        self.RequestField.setInputMask("")
        self.RequestField.setText("")
        self.RequestField.setAlignment(QtCore.Qt.AlignCenter)
        self.RequestField.setObjectName("RequestField")
        self.FileList = QtWidgets.QTextBrowser(self.centralwidget)
        self.FileList.setGeometry(QtCore.QRect(50, 50, 181, 331))
        self.FileList.setObjectName("FileList")
        self.LogList = QtWidgets.QTextBrowser(self.centralwidget)
        self.LogList.setGeometry(QtCore.QRect(300, 50, 431, 331))
        self.LogList.setObjectName("LogList")
        self.RefreshFilesButton = QtWidgets.QPushButton(self.centralwidget)
        self.RefreshFilesButton.setGeometry(QtCore.QRect(50, 400, 181, 41))
        self.RefreshFilesButton.setObjectName("RefreshFilesButton")
        self.RefreshLogsButton = QtWidgets.QPushButton(self.centralwidget)
        self.RefreshLogsButton.setGeometry(QtCore.QRect(300, 400, 431, 41))
        self.RefreshLogsButton.setObjectName("RefreshLogsButton")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.log_file = "branch_office_logs.log"
        logging.basicConfig(filename=self.log_file, level=logging.DEBUG)

        self.branch_office = BranchOffice(ip="127.0.0.1", port=5000)
        self.branch_office.connect_to_central_office()

        self.SendButton.clicked.connect(self._send_file)
        self.RequestButton.clicked.connect(self._request_file)
        self.RefreshLogsButton.clicked.connect(self._refresh_logs_field)
        self.RefreshFilesButton.clicked.connect(self._refresh_files_field)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Филиал"))
        self.SendButton.setText(_translate("MainWindow", "Отправить файл"))
        self.label_2.setText(_translate("MainWindow", "Список файлов"))
        self.label_3.setText(_translate("MainWindow", "История действий"))
        self.RequestButton.setText(_translate("MainWindow", "Запросить файл"))
        self.RequestField.setPlaceholderText(
            _translate(
                "MainWindow", "Введите название файла, который хотите запросить."
            )
        )
        self.FileList.setPlaceholderText(
            _translate(
                "MainWindow", "Здесь будет отображаться список имеющихся у вас файлов."
            )
        )
        self.LogList.setPlaceholderText(
            _translate(
                "MainWindow",
                "Здесь будет отображаться список ваших действий и действий центрального офиса по отношению к вам.",
            )
        )
        self.RefreshFilesButton.setText(
            _translate("MainWindow", "Обновить список файлов")
        )
        self.RefreshLogsButton.setText(
            _translate("MainWindow", "Обновить историю действия")
        )

    def _send_file(self):
        try:
            fname = QFileDialog.getOpenFileName(self)[0]
        except Exception as e:
            logging.error(f"Ошибка открытия файла.")
            return

        self.branch_office.send_file(fname)

    def _request_file(self):
        file_name = self.RequestField.text()

        if not file_name:
            error = QMessageBox()
            error.setWindowTitle("Ошибка")
            error.setIcon(QMessageBox.Warning)
            error.setText("Введите название файла.")
            error.exec_()
            return

        self.branch_office.request_file(file_name)

    def _refresh_files_field(self):
        directory_path = self.branch_office.files_dir
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
