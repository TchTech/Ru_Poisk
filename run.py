import subprocess
import time
import os
import platform
import logging
import multiprocessing
import sys
import requests  # Добавьте эту строку
from urllib3.exceptions import MaxRetryError

# Настройка логирования
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    stream=sys.stdout)

def is_django_server_ready(url, max_retries=10, retry_delay=2):
    """Проверяет, доступен ли Django server по указанному URL."""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=5)  # Пробуем соединиться с таймаутом
            response.raise_for_status()  # Вызывает исключение для кодов 4xx/5xx
            logging.info(f"Django server готов к работе: {url}")
            return True
        except requests.exceptions.RequestException as e:
            logging.debug(f"Попытка {attempt + 1} провалилась: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)  # Ждем перед следующей попыткой
            else:
                logging.error(f"Django server не доступен после {max_retries} попыток: {e}")
                return False
        except Exception as e:
            logging.error(f"Произошла непредвиденная ошибка при проверке доступности сервера: {e}")
            return False
    return False

def run_django_server():
    """Запускает Django development server на порту 8080 и логирует вывод."""
    try:
        logging.info("Запуск Django development server...")
        manage_py_path = os.path.abspath("manage.py")

        process = subprocess.Popen(['python', manage_py_path, 'runserver', '8080'],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT,
                                   text=True,
                                   bufsize=1)

        logging.info("Django development server запущен. Ожидаем готовность...")
        # Логирование вывода в реальном времени (как раньше)
        for line in iter(process.stdout.readline, ''):
            logging.info(f"Django: {line.strip()}")

        process.wait()  # Ожидание завершения процесса
        if process.returncode != 0:
            logging.error(f"Django development server завершился с кодом ошибки: {process.returncode}")


    except FileNotFoundError:
        logging.error(f"Файл 'manage.py' не найден")
    except Exception as e:
        logging.exception(f"Произошла ошибка при запуске Django development server: {e}")


def run_electron_app():
    """Запускает Electron app."""
    electron_app_path = 'electronApp/ru.poisk.exe'

    try:
        logging.info(f"Запуск Electron app: {electron_app_path}")
        # Проверка существования файла перед запуском
        if not os.path.exists(electron_app_path):
            logging.error(f"Electron app не найден по пути: {electron_app_path}")
            return

        # Определение команды для запуска Electron app в зависимости от ОС
        if platform.system() == "Windows":
            command = ['start', electron_app_path]  # Windows
        elif platform.system() == "Darwin":  # macOS
            command = ['open', electron_app_path]
        else:  # Linux
            command = [electron_app_path]

        process = subprocess.Popen(command, shell=True)
        logging.info("Electron app запущен.")

        process.wait()
        if process.returncode != 0:
            logging.error(f"Electron app завершился с кодом ошибки: {process.returncode}")

    except FileNotFoundError:
        logging.error(f"Electron app не найден по пути: {electron_app_path}")
    except Exception as e:
        logging.exception(f"Произошла ошибка при запуске Electron app: {e}")


if __name__ == "__main__":
    django_process = multiprocessing.Process(target=run_django_server)
    electron_process = multiprocessing.Process(target=run_electron_app)

    # Запуск Django server
    django_process.start()

    # Ждем, пока Django server не будет готов
    django_url = "http://127.0.0.1:8080/"  #  или "http://localhost:8080/"
    if is_django_server_ready(django_url):
        # Django server готов, запускаем Electron
        electron_process.start()
    else:
        logging.error("Не удалось запустить Electron app, так как Django server не был запущен.")

    # Ожидание завершения процессов
    django_process.join()
    if electron_process.is_alive(): # Проверяем, был ли запущен electron
        electron_process.join()

    logging.info("Все процессы завершены.")