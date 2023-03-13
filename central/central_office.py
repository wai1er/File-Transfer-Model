import socket
import threading
import logging
import os
import time
from Crypto.Random import get_random_bytes
from magma import encrypt_data, decrypt_data


class CentralOffice:
    def __init__(self, ip="127.0.0.1", port=5000):
        self.ip = ip
        self.port = port
        self.branch_offices = {}
        self.session_keys = {}

        self.max_buff_size = 1024
        self.send_flag = "s"
        self.request_flag = "r"
        self.recieved_flag = "+"
        self.file_not_found_flag = "-"
        self.host_error = "[WinError 10054] Удаленный хост принудительно разорвал существующее подключение"

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.ip, self.port))
        self.socket.listen()

        if not (os.path.exists("central_office_files")):
            os.mkdir("central_office_files")

        self.log_file = "central_office_logs.log"
        self.files_dir = "central_office_files"

        logging.basicConfig(filename=self.log_file, level=logging.DEBUG)
        logging.info("Центральный офис начал работу.")
        threading.Thread(target=self._listen_for_branch_offices).start()

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

    def __send_message_recieved(self, file_name: str, branch_id: str) -> None:
        branch_socket = self.branch_offices[branch_id]

        flag_file_name = (self.recieved_flag + file_name).encode()
        encrypted_file_name = encrypt_data(flag_file_name, self.session_keys[branch_id])

        branch_socket.sendall(encrypted_file_name)

    def __send_file_not_found(self, file_name: str, branch_id: str) -> None:
        branch_socket = self.branch_offices[branch_id]

        flag_file_name = (self.file_not_found_flag + file_name).encode()
        encrypted_file_name = encrypt_data(flag_file_name, self.session_keys[branch_id])

        branch_socket.sendall(encrypted_file_name)

    def _listen_for_branch_offices(self) -> None:
        while True:
            branch_socket, branch_address = self.socket.accept()
            branch_id = self._generate_id()
            session_key = self._generate_session_key()
            logging.info(
                f"Подключился новый филиал с ID {branch_id} и сессионным ключом {session_key.hex()}."
            )
            if not (os.path.exists(f"{self.files_dir}/{branch_id}")):
                os.mkdir(f"{self.files_dir}/{branch_id}")
            self.branch_offices[branch_id] = branch_socket
            self.session_keys[branch_id] = session_key

            branch_socket.sendall(session_key)

            threading.Thread(
                target=self._listen_for_requests, args=(branch_id,)
            ).start()

    def _listen_for_requests(self, branch_id: str) -> None:
        branch_socket = self.branch_offices[branch_id]
        while True:
            time.sleep(1)
            try:

                all_data_bytes = b""
                file_name = ""
                flag = None

                while True:
                    data_bytes = branch_socket.recv(self.max_buff_size)
                    if not flag:

                        decrypted_data = decrypt_data(
                            data_bytes, self.session_keys[branch_id]
                        ).decode()

                        message_len, flag, file_name = self._parse_meta_data(
                            decrypted_data
                        )

                        if flag == self.request_flag:
                            file_to_send = f"{self.files_dir}/{branch_id}/{file_name}"
                            if os.path.exists(file_to_send):
                                self.send_file(file_to_send, branch_id)
                                flag = None
                                break
                            else:
                                self.__send_file_not_found(file_name, branch_id)
                                logging.info(
                                    f"Файл {file_name} не найден для филиала {branch_id}."
                                )
                                break

                        elif flag == self.recieved_flag:
                            logging.info(
                                f"Филиал {branch_id} успешно получил файл {file_name}."
                            )
                            flag = None
                            break

                        elif flag == self.file_not_found_flag:
                            logging.info(
                                f"Филиалу {branch_id} не удалось найти файл {file_name}."
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
                        all_data_bytes, self.session_keys[branch_id]
                    )
                    print(len(all_data_bytes))
                    with open(
                        f"{self.files_dir}/{branch_id}/{file_name}", "wb"
                    ) as file:
                        file.write(decrypted_data_bytes)
                    flag = None
                    self.__send_message_recieved(file_name, branch_id)
                    logging.info(
                        f"Новый файл {file_name} получен от филиала {branch_id}."
                    )

            except Exception as e:
                logging.error(f"Ошибка запроса от филиала: {branch_id}: {str(e)}.")

                if str(e) == self.host_error:
                    break

                continue

    def _generate_id(self) -> str:
        return str(len(self.branch_offices) + 1)

    def _generate_session_key(self) -> bytes:
        return get_random_bytes(32)

    def send_file(self, file_path: str, branch_id: str) -> None:
        branch_socket = self.branch_offices[branch_id]
        file_name = os.path.basename(file_path)

        with open(file_path, "rb") as file:
            data_bytes = file.read()

        encrypted_data_bytes = encrypt_data(data_bytes, self.session_keys[branch_id])
        meta_data = (
            str(len(encrypted_data_bytes)) + self.send_flag + file_name
        ).encode()
        encrypted_meta_data = encrypt_data(meta_data, self.session_keys[branch_id])

        branch_socket.sendall(encrypted_meta_data)
        branch_socket.sendall(encrypted_data_bytes)

        logging.info(f"Файл {file_path} отправлен филиалу {branch_id}.")

    def request_file(self, file_path: str, branch_id: str) -> None:
        branch_socket = self.branch_offices[branch_id]
        file_name = os.path.basename(file_path)
        flag_file_name = (self.request_flag + file_name).encode()
        encrypted_file_name = encrypt_data(flag_file_name, self.session_keys[branch_id])

        branch_socket.sendall(encrypted_file_name)

        logging.info(f"Запрос файла {file_path} у филиала {branch_id}.")


if __name__ == "__main__":
    central = CentralOffice()
    while True:
        filename = input()
        central.request_file(filename, "1")
