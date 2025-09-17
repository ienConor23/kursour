import socket
import json
import webbrowser
import requests
import logging
import time
import os
import tempfile
import subprocess
import threading
import math
import random
from datetime import datetime
from bs4 import BeautifulSoup
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
from hachoir.core.tools import makePrintable
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QWidget, QMessageBox,
                             QTextEdit, QComboBox, QHBoxLayout, QFrame,
                             QTabWidget, QFileDialog, QProgressBar)
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFont, QColor, QPalette

HOST = "127.0.0.1"
PORT = 5000

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

API_TOKENS = {
    "Database_TOKEN": "sakuta_Jrhfox55jsmPpL",
    "OFDATA_TOKEN": "KBnpz1CHKNngFXxK",
    "VK_ACCESS_TOKENS": ["vk1.a.HeDl8lqHjH_r3tPWybVdVpIWJz6Ks9qg_bdlZNMbzv8gMK67GbIM6nmUj8ZlL_RJFwqP9Kx5Y1MBwpawmHuZYfOIJZbWovavuRYof0LZZ1yznfPxEmhdv3jxXtGCeonME_AJgnlghgZtrRdTemWZRTX75BmTg3X8V3LNg5VzOmG80Vf2uVkvPLdjVTQOxR2OAwWwTVEaIxKI7ps1yZm8Ig", "7277da837277da83ab72598eec772777277da832972d87340fcc725d06c3ff7"],
    "VK_API_VERSION": "5.199", 
    "FUNSTAT_TOKEN": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOiIyMDMzMDI5NDc1IiwianRpIjoiZWExZTMzMjktNWNhMS00NzVlLTg0ZjgtZTM1OGNkMzNmZDFlIiwiZXhwIjoxNzg3OTM3Njk3fQ.gXf5FfdgTY6OzYA0kgDSYY_lHp0E2eUV19Bkig09o41eFZ7XpAXoCpSQGgVXwUhrt7Q3gkiwse9K66N6MGLq0FZkDJGVI11LUetvmMDedTuUlS-DJ876LwjGeeZ8ZnINiei8ujN4C6U4iQTQhl4Qm0c4Ch_11hw17_nHEv3GFN0",
}

API_BASE_URL = "https://funstat.info/api/v1"
VK_METHODS = {
    0: {"name": "users.get", "description": "Информация о профиле", "params": ["user_ids", "fields"]},
    1: {"name": "users.search", "description": "Поиск пользователей", "params": ["q", "fields", "count", "offset"]},
}

class SearchThread(QThread):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)

    def __init__(self, search_type, query, method_id=None, params=None):
        super().__init__()
        self.search_type = search_type
        self.query = query
        self.method_id = method_id
        self.params = params

    def run(self):
        try:
            if self.search_type == "Database":
                result = self.Database_query(self.query)
            elif self.search_type == "ip":
                result = self.ip_search(self.query)
            elif self.search_type == "fio":
                result = self.fio_search(self.query)
            elif self.search_type == "vk":
                result = self.vk_search(self.query, self.method_id, self.params)
            elif self.search_type == "face":
                result = self.face_search(self.query)
            elif self.search_type == "metadata":
                result = self.metadata_analysis(self.query)
            elif self.search_type == "funstat_id":
                result = self.funstat_id_search(self.query)
            elif self.search_type == "funstat_username":
                result = self.funstat_username_search(self.query)
            
            self.finished.emit(result)
            
        except Exception as e:
            self.error.emit(str(e))

    def Database_query(self, query):
        self.progress.emit("Выполнение поиска в Database...")
        API_URL_SEARCH = f"http://api.fastsearch.digital/poisk/search={query}?token={API_TOKENS['Database_TOKEN']}"
        
        response = requests.get(API_URL_SEARCH, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Ошибка API: {response.status_code}")

    def ip_search(self, ip):
        self.progress.emit(f"Сбор информации по IP {ip}...")
        ip_info = {}
        
        services = [
            {"name": "ip-api.com", "url": f"http://ip-api.com/json/{ip}"},
            {"name": "ipinfo.io", "url": f"https://ipinfo.io/{ip}/json"},
            {"name": "ipapi.co", "url": f"https://ipapi.co/{ip}/json/"},
        ]
        
        for service in services:
            try:
                response = requests.get(service["url"], timeout=10)
                if response.status_code == 200:
                    ip_info[service["name"]] = response.json()
            except:
                continue
        
        return ip_info

    def fio_search(self, fio):
        self.progress.emit("Поиск информации по ФИО...")
        url = f"https://api.ofdata.ru/v2/search?key={API_TOKENS['OFDATA_TOKEN']}&by=founder-name&obj=org&query={fio}"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Ошибка API: {response.status_code}")

    def vk_search(self, query, method_id, params):
        self.progress.emit("Поиск в VK API...")
    
        if method_id is None:
            raise Exception("Метод VK API не выбран")
        
        method_info = VK_METHODS.get(method_id)
        if not method_info:
            raise Exception("Неизвестный метод VK API")
        
        method_name = method_info["name"]
    
        access_tokens = API_TOKENS["VK_ACCESS_TOKENS"]
        if not access_tokens:
            raise Exception("Токены VK не найдены")
        
        access_token = access_tokens[0]
        version = API_TOKENS["VK_API_VERSION"]
    
        api_url = f"https://api.vk.com/method/{method_name}"
    
        request_params = {
            "access_token": access_token,
            "v": version
        }
    
        if params:
            for param_name, param_value in params.items():
                if param_value:
                    request_params[param_name] = param_value
        
        if method_name == "users.get":
            if not request_params.get("fields"):
                request_params["fields"] = "photo_max_orig,domain,contacts,connections,site,about,activities,bdate,books,can_post,can_see_all_posts,can_see_audio,can_write_private_message,career,city,common_count,country,education,exports,first_name_gen,home_town,interests,last_name_gen,maiden_name,military,movies,music,nickname,occupation,personal,quotes,relation,relatives,schools,timezone,tv,universities"
            if query and not request_params.get("user_ids"):
                request_params["user_ids"] = query
        
        elif method_name == "users.search":
            if query and not request_params.get("q"):
                request_params["q"] = query
            if not request_params.get("count"):
                request_params["count"] = "100"
            if not request_params.get("fields"):
                request_params["fields"] = "photo_max_orig,domain,city,country,bdate,sex"

            if not request_params.get("q") and query:
                request_params["q"] = query

        try:
            response = requests.get(api_url, params=request_params, timeout=30)
            response.raise_for_status()

            data = response.json()
            if "error" in data:
                error_msg = data["error"].get("error_msg", "Неизвестная ошибка VK API")
                raise Exception(f"Ошибка VK API: {error_msg}")
            return data

        except requests.exceptions.RequestException as e:
            raise Exception(f"Ошибка сети: {e}")
        except ValueError as e:
            raise Exception(f"Ошибка парсинга JSON: {e}")

    def face_search(self, image_path):
        self.progress.emit("Поиск похожих лиц...")
        url = "https://similarfaces.me/api/search-faces"
        
        with open(image_path, 'rb') as image_file:
            files = {'image': image_file}
            response = requests.post(url, files=files, timeout=60)
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Ошибка поиска лиц: {response.status_code}")

    def metadata_analysis(self, file_path):
        self.progress.emit("Анализ метаданных файла...")
        
        if not os.path.exists(file_path):
            raise Exception("Файл не найден")
        
        parser = createParser(file_path)
        if parser is None:
            raise Exception("Невозможно проанализировать этот тип файла")
        
        try:
            with parser:
                metadata = extractMetadata(parser)
                if not metadata:
                    raise Exception("Метаданные не найдены")
                
                result = []
                for item in metadata.exportPlaintext():
                    result.append(item.strip().replace(" - ", " > "))
                
                return result
        except Exception as e:
            raise Exception(f"Ошибка при анализе: {e}")

    def funstat_id_search(self, user_id):
        self.progress.emit(f"Сбор информации по ID {user_id} с Funstat...")
        endpoints = [
        ("stats_min", f"{API_BASE_URL}/users/{user_id}/stats_min"),
        ("stats", f"{API_BASE_URL}/users/{user_id}/stats"),
        ("groups_count", f"{API_BASE_URL}/users/{user_id}/groups_count"),
        ("messages", f"{API_BASE_URL}/users/{user_id}/messages"),
        ("messages_count", f"{API_BASE_URL}/users/{user_id}/messages_count"),
        ("groups", f"{API_BASE_URL}/users/{user_id}/groups"),
        ("names", f"{API_BASE_URL}/users/{user_id}/names"),
        ("usernames", f"{API_BASE_URL}/users/{user_id}/usernames")
        ]
        
        results = {}
        headers = {"Authorization": f"Bearer {API_TOKENS['FUNSTAT_TOKEN']}"}
        
        for endpoint_name, url in endpoints:
            try:
                response = requests.get(url, headers=headers, timeout=30)
                if response.status_code == 200:
                    results[endpoint_name] = response.json()
                else:
                    results[endpoint_name] = f"Ошибка: {response.status_code}"
            except Exception as e:
                results[endpoint_name] = f"Ошибка запроса: {str(e)}"
        
        return results

    def funstat_username_search(self, username):
        self.progress.emit(f"Поиск пользователя {username} в Funstat...")
    
        url = f"{API_BASE_URL}/users/resolve_username"
        params = {"name": username}
        headers = {"Authorization": f"Bearer {API_TOKENS['FUNSTAT_TOKEN']}"}
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Ошибка API: {response.status_code}")
        except Exception as e:
            raise Exception(f"Ошибка запроса: {str(e)}")

class AuthWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        logging.info("Инициализация окна авторизации")
        self.setWindowTitle("Arasaka Tool - Авторизация")
        self.setGeometry(100, 100, 400, 200)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout()

        self.token_label = QLabel("Введите токен:")
        layout.addWidget(self.token_label)

        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("Токен авторизации")
        layout.addWidget(self.token_input)

        self.user_id_label = QLabel("Введите user_id:")
        layout.addWidget(self.user_id_label)

        self.user_id_input = QLineEdit()
        self.user_id_input.setPlaceholderText("ID пользователя")
        layout.addWidget(self.user_id_input)

        self.auth_button = QPushButton("Войти")
        self.auth_button.clicked.connect(self.check_token)
        layout.addWidget(self.auth_button)

        self.telegram_button = QPushButton("Получить токен в Telegram")
        self.telegram_button.clicked.connect(self.open_telegram_bot)
        layout.addWidget(self.telegram_button)

        self.central_widget.setLayout(layout)

        self.check_token_periodically()

    def open_telegram_bot(self):
        webbrowser.open("https://t.me/noripidoras")

    def check_token(self):
        token = self.token_input.text()
        user_id = self.user_id_input.text()  
        logging.info(f"Проверка токена: {token}, user_id: {user_id}")
        if not token or not user_id:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите токен и user_id.")
            logging.warning("Токен или user_id не введены пользователем")
            return

        self.thread = TokenCheckThread(token, user_id)
        self.thread.result_signal.connect(self.handle_token_check_result)
        self.thread.start()

    def handle_token_check_result(self, result):
        if "message" in result:
            QMessageBox.information(self, "Успех", "Токен валиден! Добро пожаловать.")
            logging.info("Токен успешно проверен")
            self.open_main_window()
        else:
            QMessageBox.warning(self, "Ошибка", f"Ошибка: {result.get('error')}")
            logging.warning(f"Ошибка проверки токена: {result.get('error')}")

    def open_main_window(self):
        logging.info("Открытие главного окна")
        self.main_window = MainWindow()
        self.main_window.show()
        self.close()

    def check_token_periodically(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.sync_token_status)
        self.timer.start(300000)  

    def sync_token_status(self):
        try:
            response = requests.post("http://localhost:5000/verify_token", json={"token": self.token_input.text()})
            if response.status_code != 200:
                QMessageBox.warning(self, "Ошибка", "Ваш токен больше не действителен. Получите новый токен.")
                self.open_telegram_bot()
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка соединения: {e}")

class TokenCheckThread(QThread):
    result_signal = pyqtSignal(dict)

    def __init__(self, token, user_id):
        super(TokenCheckThread, self).__init__()
        self.token = token
        self.user_id = user_id

    def run(self):
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((HOST, PORT))
            request = json.dumps({"token": self.token, "user_id": self.user_id}).encode("utf-8")
            client_socket.send(request)
            response = client_socket.recv(1024).decode("utf-8")
            client_socket.close()
            response_data = json.loads(response)
            self.result_signal.emit(response_data)
        except Exception as e:
            self.result_signal.emit({"error": str(e)})

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        logging.info("Инициализация главного окна")
        self.setWindowTitle("Arasaka OSINT Tool")
        self.setGeometry(100, 100, 1000, 700)

        self.setup_ui()
        self.setup_styles()

    def setup_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        main_layout = QVBoxLayout()

        self.tab_widget = QTabWidget()
        
        self.create_Database_tab()
        self.create_ip_search_tab()
        self.create_fio_search_tab()
        self.create_vk_search_tab()
        self.create_face_search_tab()
        self.create_metadata_tab()
        self.create_funstat_tab()

        main_layout.addWidget(self.tab_widget)

        self.status_label = QLabel("Система активирована | Готов к работе")
        main_layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        self.central_widget.setLayout(main_layout)

    def setup_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0a0a0a;
            }
            QTabWidget::pane {
                border: 2px solid #00ff88;
                background: #001111;
            }
            QTabBar::tab {
                background: #002222;
                color: #00ff88;
                padding: 10px;
                border: 1px solid #00ff88;
                font-family: Consolas;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: #003333;
                color: #00ffcc;
            }
            QLabel {
                color: #00ff88;
                font-family: Consolas;
            }
            QLineEdit {
                background: #002222;
                color: #00ff88;
                border: 1px solid #00ff88;
                padding: 5px;
                font-family: Consolas;
            }
            QPushButton {
                background: #002222;
                color: #00ff88;
                border: 2px solid #00ff88;
                padding: 8px;
                font-family: Consolas;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #003333;
                color: #00ffcc;
            }
            QTextEdit {
                background: #161b22;
                color: #ffcc00;
                border: 1px solid #00ff88;
                font-family: 'Fira Code';
            }
            QComboBox {
                background: #002222;
                color: #00ff88;
                border: 1px solid #00ff88;
                padding: 5px;
                font-family: Consolas;
            }
        """)

    def create_Database_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        frame = QFrame()
        frame_layout = QVBoxLayout()

        input_layout = QHBoxLayout()
        self.Database_var = QLineEdit()
        self.Database_var.setPlaceholderText("Введите запрос для поиска...")
        input_layout.addWidget(self.Database_var)

        search_btn = QPushButton("Поиск")
        search_btn.clicked.connect(self.run_Database)
        input_layout.addWidget(search_btn)

        frame_layout.addLayout(input_layout)

        self.Database_results = QTextEdit()
        self.Database_results.setFont(QFont("Fira Code", 11))
        frame_layout.addWidget(self.Database_results)

        frame.setLayout(frame_layout)
        layout.addWidget(frame)
        tab.setLayout(layout)

        self.tab_widget.addTab(tab, "Универсальный поиск")

    def create_ip_search_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        frame = QFrame()
        frame_layout = QVBoxLayout()

        input_layout = QHBoxLayout()
        self.ip_var = QLineEdit()
        self.ip_var.setPlaceholderText("Введите IP адрес...")
        input_layout.addWidget(self.ip_var)

        search_btn = QPushButton("Поиск")
        search_btn.clicked.connect(self.run_ip_search)
        input_layout.addWidget(search_btn)

        frame_layout.addLayout(input_layout)

        self.ip_results = QTextEdit()
        self.ip_results.setFont(QFont("Fira Code", 11))
        self.ip_results.setStyleSheet("color: #00ffcc;")
        frame_layout.addWidget(self.ip_results)

        frame.setLayout(frame_layout)
        layout.addWidget(frame)
        tab.setLayout(layout)

        self.tab_widget.addTab(tab, "Поиск по IP")

    def create_fio_search_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        frame = QFrame()
        frame_layout = QVBoxLayout()

        input_layout = QHBoxLayout()
        self.fio_var = QLineEdit()
        self.fio_var.setPlaceholderText("Введите ФИО...")
        input_layout.addWidget(self.fio_var)

        search_btn = QPushButton("Поиск")
        search_btn.clicked.connect(self.run_fio_search)
        input_layout.addWidget(search_btn)

        frame_layout.addLayout(input_layout)

        self.fio_results = QTextEdit()
        self.fio_results.setFont(QFont("Fira Code", 11))
        self.fio_results.setStyleSheet("color: #0066ff;")
        frame_layout.addWidget(self.fio_results)

        frame.setLayout(frame_layout)
        layout.addWidget(frame)
        tab.setLayout(layout)

        self.tab_widget.addTab(tab, "Поиск по ФИО")

    def create_vk_search_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        frame = QFrame()
        frame_layout = QVBoxLayout()

        method_layout = QHBoxLayout()
        method_layout.addWidget(QLabel("Метод API:"))

        self.vk_method_combo = QComboBox()
        for i, method in VK_METHODS.items():
            self.vk_method_combo.addItem(f"{i}: {method['description']}", i)
        self.vk_method_combo.currentIndexChanged.connect(self.on_vk_method_changed)
        method_layout.addWidget(self.vk_method_combo)

        frame_layout.addLayout(method_layout)

        input_layout = QHBoxLayout()
        self.vk_var = QLineEdit()
        self.vk_var.setPlaceholderText("Введите запрос...")
        input_layout.addWidget(self.vk_var)

        search_btn = QPushButton("Поиск")
        search_btn.clicked.connect(self.run_vk_search)
        input_layout.addWidget(search_btn)

        frame_layout.addLayout(input_layout)

        self.params_frame = QFrame()
        self.params_layout = QVBoxLayout()
        self.params_frame.setLayout(self.params_layout)
        frame_layout.addWidget(self.params_frame)

        self.vk_results = QTextEdit()
        self.vk_results.setFont(QFont("Fira Code", 11))
        self.vk_results.setStyleSheet("color: #00ff66;")
        frame_layout.addWidget(self.vk_results)

        frame.setLayout(frame_layout)
        layout.addWidget(frame)
        tab.setLayout(layout)

        self.tab_widget.addTab(tab, "Поиск в VK")
        self.on_vk_method_changed()

    def create_face_search_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        frame = QFrame()
        frame_layout = QVBoxLayout()

        file_layout = QHBoxLayout()
        self.face_file_var = QLineEdit()
        self.face_file_var.setPlaceholderText("Путь к изображению...")
        file_layout.addWidget(self.face_file_var)

        browse_btn = QPushButton("Обзор")
        browse_btn.clicked.connect(self.browse_face_image)
        file_layout.addWidget(browse_btn)

        frame_layout.addLayout(file_layout)

        search_btn = QPushButton("Найти похожие лица")
        search_btn.clicked.connect(self.run_face_search)
        frame_layout.addWidget(search_btn)

        self.face_results = QTextEdit()
        self.face_results.setFont(QFont("Fira Code", 11))
        self.face_results.setStyleSheet("color: #ff6600;")
        frame_layout.addWidget(self.face_results)

        frame.setLayout(frame_layout)
        layout.addWidget(frame)
        tab.setLayout(layout)

        self.tab_widget.addTab(tab, "Поиск по лицу")

    def create_metadata_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        frame = QFrame()
        frame_layout = QVBoxLayout()

        file_layout = QHBoxLayout()
        self.metadata_file_var = QLineEdit()
        self.metadata_file_var.setPlaceholderText("Путь к файлу...")
        file_layout.addWidget(self.metadata_file_var)

        browse_btn = QPushButton("Обзор")
        browse_btn.clicked.connect(self.browse_metadata_file)
        file_layout.addWidget(browse_btn)

        frame_layout.addLayout(file_layout)

        analyze_btn = QPushButton("Анализировать метаданные")
        analyze_btn.clicked.connect(self.run_metadata_analysis)
        frame_layout.addWidget(analyze_btn)

        self.metadata_results = QTextEdit()
        self.metadata_results.setFont(QFont("Fira Code", 11))
        self.metadata_results.setStyleSheet("color: #cc00ff;")
        frame_layout.addWidget(self.metadata_results)

        frame.setLayout(frame_layout)
        layout.addWidget(frame)
        tab.setLayout(layout)

        self.tab_widget.addTab(tab, "Анализ метаданных")

    def create_funstat_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        frame = QFrame()
        frame_layout = QVBoxLayout()

        method_layout = QHBoxLayout()
        method_layout.addWidget(QLabel("Тип поиска:"))

        self.funstat_search_type = QComboBox()
        self.funstat_search_type.addItems(["id", "username"])
        method_layout.addWidget(self.funstat_search_type)

        frame_layout.addLayout(method_layout)

        input_layout = QHBoxLayout()
        self.funstat_var = QLineEdit()
        self.funstat_var.setPlaceholderText("Введите запрос...")
        input_layout.addWidget(self.funstat_var)

        search_btn = QPushButton("Запуск поиска")
        search_btn.clicked.connect(self.run_funstat_search)
        input_layout.addWidget(search_btn)

        frame_layout.addLayout(input_layout)

        self.funstat_results = QTextEdit()
        self.funstat_results.setFont(QFont("Fira Code", 11))
        self.funstat_results.setStyleSheet("color: #ff99cc;")
        frame_layout.addWidget(self.funstat_results)

        frame.setLayout(frame_layout)
        layout.addWidget(frame)
        tab.setLayout(layout)

        self.tab_widget.addTab(tab, "Funstat")

    def on_vk_method_changed(self):
        for i in reversed(range(self.params_layout.count())): 
            self.params_layout.itemAt(i).widget().setParent(None)

        method_id = self.vk_method_combo.currentData()
        if method_id is None:
            return

        method_info = VK_METHODS.get(method_id)
        if not method_info:
            return

        params = method_info.get("params", [])
        self.vk_param_vars = {}

        for param in params:
            param_layout = QHBoxLayout()
            param_layout.addWidget(QLabel(f"{param}:"))
            
            var = QLineEdit()
            self.vk_param_vars[param] = var
            param_layout.addWidget(var)
            
            self.params_layout.addLayout(param_layout)

    def browse_face_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите изображение", "", "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            self.face_file_var.setText(file_path)

    def browse_metadata_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите файл для анализа", ""
        )
        if file_path:
            self.metadata_file_var.setText(file_path)

    def run_Database(self):
        query = self.Database_var.text().strip()
        if not query:
            QMessageBox.warning(self, "Ошибка", "Введите запрос для поиска")
            return
            
        self.update_status("Выполняется поиск...")
        self.start_search_thread("Database", query)

    def run_ip_search(self):
        ip = self.ip_var.text().strip()
        if not ip:
            QMessageBox.warning(self, "Ошибка", "Введите IP адрес")
            return
            
        self.update_status(f"Сбор информации по IP {ip}...")
        self.start_search_thread("ip", ip)

    def run_fio_search(self):
        fio = self.fio_var.text().strip()
        if not fio:
            QMessageBox.warning(self, "Ошибка", "Введите ФИО")
            return
            
        self.update_status("Поиск информации по ФИО...")
        self.start_search_thread("fio", fio)

    def run_vk_search(self):
        query = self.vk_var.text().strip()
        method_id = self.vk_method_combo.currentData()

        if method_id is None:
            QMessageBox.warning(self, "Ошибка", "Выберите метод VK API")
            return

        method_info = VK_METHODS.get(method_id)
        if not method_info:
            QMessageBox.warning(self, "Ошибка", "Неизвестный метод VK API")
            return

        method_name = method_info["name"]

        if method_name == "users.get" and not query:
            QMessageBox.warning(self, "Ошибка", "Введите ID пользователя или screen_name")
            return
        elif method_name == "users.search" and not query:
            QMessageBox.warning(self, "Ошибка", "Введите запрос для поиска")
            return

        params = {}
        for param_name, widget in self.vk_param_vars.items():
            value = widget.text().strip()
            if value:
                params[param_name] = value

        self.update_status("Выполняется поиск в VK...")
        self.start_search_thread("vk", query, method_id, params)

    def run_face_search(self):
        file_path = self.face_file_var.text().strip()
        if not file_path or not os.path.exists(file_path):
            QMessageBox.warning(self, "Ошибка", "Выберите корректный файл изображения")
            return
            
        self.update_status("Поиск похожих лиц...")
        self.start_search_thread("face", file_path)

    def run_metadata_analysis(self):
        file_path = self.metadata_file_var.text().strip()
        if not file_path or not os.path.exists(file_path):
            QMessageBox.warning(self, "Ошибка", "Выберите корректный файл")
            return
            
        self.update_status("Анализ метаданных файла...")
        self.start_search_thread("metadata", file_path)

    def run_funstat_search(self):
        query = self.funstat_var.text().strip()
        search_type = self.funstat_search_type.currentText()

        if not query:
            QMessageBox.warning(self, "Ошибка", "Введите запрос для поиска")
            return

        if search_type == "id":
            self.update_status(f"Сбор информации по ID {query}...")
            self.start_search_thread("funstat_id", query)
        else:
            self.update_status(f"Поиск пользователя {query}...")
            self.start_search_thread("funstat_username", query)

    def start_search_thread(self, search_type, query, method_id=None, params=None):
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)

        self.thread = SearchThread(search_type, query, method_id, params)
        self.thread.finished.connect(self.on_search_finished)
        self.thread.error.connect(self.on_search_error)
        self.thread.progress.connect(self.update_status)
        self.thread.start()

    def on_search_finished(self, result):
        self.progress_bar.setVisible(False)
        
        current_tab = self.tab_widget.currentIndex()
        
        if current_tab == 0:
            text_widget = self.Database_results
            formatted = self.format_Database_result(result)
        elif current_tab == 1:
            text_widget = self.ip_results
            formatted = self.format_ip_result(result)
        elif current_tab == 2:
            text_widget = self.fio_results
            formatted = self.format_fio_result(result)
        elif current_tab == 3:
            text_widget = self.vk_results
            formatted = self.format_vk_result(result)
        elif current_tab == 4:
            text_widget = self.face_results
            formatted = self.format_face_result(result)
        elif current_tab == 5:
            text_widget = self.metadata_results
            formatted = "\n".join(result) if isinstance(result, list) else str(result)
        elif current_tab == 6:
            text_widget = self.funstat_results
            formatted = self.format_funstat_result(result)
        else:
            return

        text_widget.setPlainText(formatted)
        self.update_status("Поиск завершен успешно")

    def on_search_error(self, error_msg):
        self.progress_bar.setVisible(False)
        self.update_status(f"Ошибка: {error_msg}")
        QMessageBox.critical(self, "Ошибка", f"Произошла ошибка:\n{error_msg}")

    def update_status(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_label.setText(f"[{timestamp}] {message}")

    def format_Database_result(self, data):
        if not data or 'results' not in data or not data['results']:
            return "По данному запросу ничего не найдено"
        
        result_text = "РЕЗУЛЬТАТЫ\n\n"
        
        for i, item in enumerate(data['results'], 1):
            result_text += f"РЕЗУЛЬТАТ #{i}\n"
            
            for key, value in item.items():
                pretty_key = {
                    'ФАМИЛИЯ': 'Фамилия',
                    'ИМЯ': 'Имя',
                    'ДАТА РОЖДЕНИЯ': 'Дата рождения',
                    'email': 'Email',
                    'phone': 'Телефон',
                    'collection': 'Источник данных'
                }.get(key, key)
                
                result_text += f"{pretty_key}: {value}\n"
            
            result_text += "\n"
        
        if 'search_time_seconds' in data:
            search_time = float(data['search_time_seconds'])
            result_text += f"\nПоиск выполнен за {search_time:.2f} секунд\n"
        
        return result_text

    def format_ip_result(self, data):
        if not data:
            return "Не удалось получить информацию по IP"
        
        result_text = "РЕЗУЛЬТАТЫ ПОИСКА ПО IP\n\n"
        
        for service_name, service_data in data.items():
            result_text += f"=== {service_name.upper()} ===\n"
            
            if isinstance(service_data, dict):
                for key, value in service_data.items():
                    if value:
                        result_text += f"{key}: {value}\n"
            else:
                result_text += f"{service_data}\n"
            
            result_text += "\n"
        
        return result_text

    def format_fio_result(self, data):
        if not data or 'data' not in data or not data['data']:
            return "По данному ФИО ничего не найдено"
        
        result_text = "РЕЗУЛЬТАТЫ ПОИСКА ПО ФИО\n\n"
        
        for i, item in enumerate(data['data'], 1):
            result_text += f"РЕЗУЛЬТАТ #{i}\n"
            
            if 'name' in item:
                result_text += f"ФИО: {item['name']}\n"
            if 'inn' in item:
                result_text += f"ИНН: {item['inn']}\n"
            if 'ogrn' in item:
                result_text += f"ОГРН: {item['ogrn']}\n"
            if 'status' in item:
                result_text += f"Статус: {item['status']}\n"
            if 'registration_date' in item:
                result_text += f"Дата регистрации: {item['registration_date']}\n"
            
            result_text += "\n"
        
        return result_text

    def format_vk_result(self, data):
        if not data:
            return "Нет данных"
        
        result_text = "РЕЗУЛЬТАТЫ ПОИСКА VK\n\n"
        
        if 'response' in data:
            response = data['response']
            
            if isinstance(response, dict):
                if 'count' in response and 'items' in response:
                    result_text += f"Найдено результатов: {response['count']}\n\n"
                    
                    for i, item in enumerate(response['items'], 1):
                        result_text += f"РЕЗУЛЬТАТ #{i}\n"
                        result_text += self.format_vk_user(item)
                        result_text += "\n"
                else:
                    result_text += str(response)
            elif isinstance(response, list):
                for i, item in enumerate(response, 1):
                    result_text += f"РЕЗУЛЬТАТ #{i}\n"
                    if isinstance(item, dict):
                        result_text += self.format_vk_user(item)
                    else:
                        result_text += str(item)
                    result_text += "\n"
            else:
                result_text += str(response)
        else:
            result_text += str(data)
        
        return result_text

    def format_vk_user(self, user):
        text = ""
        
        if 'id' in user:
            text += f"ID: {user['id']}\n"
        if 'first_name' in user:
            text += f"Имя: {user['first_name']}\n"
        if 'last_name' in user:
            text += f"Фамилия: {user['last_name']}\n"
        if 'screen_name' in user:
            text += f"Ссылка: vk.com/{user['screen_name']}\n"
        if 'bdate' in user:
            text += f"Дата рождения: {user['bdate']}\n"
        if 'city' in user and 'title' in user['city']:
            text += f"Город: {user['city']['title']}\n"
        if 'country' in user and 'title' in user['country']:
            text += f"Страна: {user['country']['title']}\n"
        if 'photo_max_orig' in user:
            text += f"Фото: {user['photo_max_orig']}\n"
        if 'domain' in user:
            text += f"Домен: {user['domain']}\n"
        
        return text

    def format_face_result(self, data):
        if not data or 'results' not in data or not data['results']:
            return "Похожие лица не найдены"
        
        result_text = "РЕЗУЛЬТАТЫ ПОИСКА ПО ЛИЦУ\n\n"
        result_text += f"Найдено совпадений: {len(data['results'])}\n\n"
        
        for i, result in enumerate(data['results'], 1):
            result_text += f"СОВПАДЕНИЕ #{i}\n"
            result_text += f"Ссылка: {result.get('url', 'N/A')}\n"
            result_text += f"Сходство: {result.get('similarity', 'N/A')}%\n"
            result_text += f"Источник: {result.get('source', 'N/A')}\n"
            result_text += "\n"
        
        return result_text

    def format_funstat_result(self, data):
        if not data:
            return "Нет данных"
        
        result_text = "РЕЗУЛЬТАТЫ FUNSTAT\n\n"
        
        if isinstance(data, dict):
            for key, value in data.items():
                result_text += f"=== {key.upper()} ===\n"
                
                if isinstance(value, dict):
                    for subkey, subvalue in value.items():
                        result_text += f"{subkey}: {subvalue}\n"
                elif isinstance(value, list):
                    for i, item in enumerate(value, 1):
                        result_text += f"{i}. {item}\n"
                else:
                    result_text += f"{value}\n"
                
                result_text += "\n"
        else:
            result_text += str(data)
        
        return result_text

def main():
    app = QApplication([])
    
    auth_window = AuthWindow()
    auth_window.show()
    
    app.exec_()

if __name__ == "__main__":
    main()