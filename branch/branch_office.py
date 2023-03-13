import socket
import os
import threading
import logging
from magma import encrypt_data, decrypt_data


class BranchOffice:
    def __init__(self, ip="127.0.0.1", port=5000):
        self.ip = ip
        self.port = port
        self.session_key = None

        self.max_buff_size = 1024
        self.send_flag = "s"
        self.requset_flag = "r"
        self.recieved_flag = "+"
        self.file_not_found_flag = "-"
        self.host_error = "[WinError 10054] Удаленный хост принудительно разорвал существующее подключение"

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if not (os.path.exists("branch_office_files")):
            os.mkdir("branch_office_files")

        self.log_file = "branch_office_logs.log"
        self.files_dir = "branch_office_files"

        logging.basicConfig(filename=self.log_file, level=logging.DEBUG)

    def connect_to_central_office(
        self, central_ip="127.0.0.1", central_port=5000
    ) -> None:
        self.socket.connect((central_ip, central_port))
        logging.info("Подключен к центральному офису.")
        self.session_key = self._receive_session_key()
        logging.info(f"Получен сессионный ключ {self.session_key}.")
        threading.Thread(target=self._listen_for_requests).start()

    def __send_message_recieved(self, file_name: str) -> None:
        flag_file_name = (self.recieved_flag + file_name).encode()
        encrypted_file_name = encrypt_data(flag_file_name, self.session_key)
        self.socket.sendall(encrypted_file_name)

    def __send_file_not_found(self, file_name: str) -> None:
        flag_file_name = (self.file_not_found_flag + file_name).encode()
        encrypted_file_name = encrypt_data(flag_file_name, self.session_key)
        self.socket.sendall(encrypted_file_name)

    def _receive_session_key(self) -> None:
        session_key_bytes = self.socket.recv(1024)
        return session_key_bytes

    def _parse_meta_data(self, meta_data):
        if meta_data[0].isdigit():
            meta_end_index = next(
                (i for i, c in enumerate(meta_data) if not c.isdigit()), None
            )
            metadata_len = int(meta_data[:meta_end_index])
            flag = meta_data[meta_end_index]
            file_name = meta_data[meta_end_index + 1 :]
        else:
            flag = meta_data[0]
            file_name = meta_data[1:]
            metadata_len = 0
        return metadata_len, flag, file_name

    def _listen_for_requests(self) -> None:
        while True:
            try:
                all_data_bytes = b""
                file_name = ""
                flag = None

                while True:
                    data_bytes = self.socket.recv(self.max_buff_size)

                    if not flag:
                        decrypted_data = decrypt_data(
                            data_bytes, self.session_key
                        ).decode()

                        message_len, flag, file_name = self._parse_meta_data(
                            decrypted_data
                        )

                        if flag == self.requset_flag:
                            file_to_send = f"{self.files_dir}/{file_name}"
                            if os.path.exists(file_to_send):
                                self.send_file(file_to_send)
                                flag = None
                                break
                            else:
                                self.__send_file_not_found(file_name)
                                logging.info(f"Файл {file_name} не найден.")
                                break

                        elif flag == self.recieved_flag:
                            logging.info(
                                f"Центральный офис успешно получил файл {file_name}."
                            )
                            flag = None
                            break

                        elif flag == self.file_not_found_flag:
                            logging.info(
                                f"Центральному офису не удалось найти файл {file_name}."
                            )
                            flag = None
                            break

                    else:
                        if flag == self.send_flag:
                            all_data_bytes += data_bytes

                        if len(all_data_bytes) == message_len:
                            break

                if flag == self.send_flag:
                    decrypted_data_bytes = decrypt_data(
                        all_data_bytes, self.session_key
                    )

                    with open(f"{self.files_dir}/{file_name}", "wb") as file:
                        file.write(decrypted_data_bytes)
                    flag = None

                    self.__send_message_recieved(file_name)
                    logging.info(f"Файл {file_name} получен от центрального офиса.")

            except Exception as e:
                logging.error(f"Ошибка запроса от центрального офиса: {str(e)}.")
                if str(e) == self.host_error:
                    break
                continue

    def send_file(self, file_path: str) -> None:
        file_name = os.path.basename(file_path)

        with open(file_path, "rb") as file:
            data_bytes = file.read()

        encrypted_data_bytes = encrypt_data(data_bytes, self.session_key)
        meta_data = (
            str(len(encrypted_data_bytes)) + self.send_flag + file_name
        ).encode()
        encrypted_meta_data = encrypt_data(meta_data, self.session_key)

        self.socket.sendall(encrypted_meta_data)
        self.socket.sendall(encrypted_data_bytes)

        logging.info(f"Файл {file_path} отправлен центральному офису.")

    def request_file(self, file_path: str) -> None:
        file_name = os.path.basename(file_path)
        flag_file_name = (self.requset_flag + file_name).encode()
        encrypted_file_name = encrypt_data(flag_file_name, self.session_key)

        self.socket.sendall(encrypted_file_name)

        logging.info(f"Запрос файла {file_path} у центрального сервера.")


if __name__ == "__main__":
    branch_office = BranchOffice(ip="127.0.0.1", port=5000)
    branch_office.connect_to_central_office()

    while True:
        filename = input()
        branch_office.request_file(filename)
