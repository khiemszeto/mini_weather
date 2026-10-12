import os
import sys

import requests
from PySide6.QtWidgets import QApplication, QWidget,QLabel, QLineEdit, QPushButton, QVBoxLayout
from PySide6.QtCore import Qt

def load_api_key():
    key = os.environ.get("OPENWEATHER_API_KEY", "").strip()
    if key:
        return key

    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if not os.path.isfile(env_path):
        return ""

    with open(env_path, encoding="utf-8") as env_file:
        for line in env_file:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            name, value = line.split("=", 1)
            if name.strip() == "OPENWEATHER_API_KEY":
                return value.strip().strip('"').strip("'")
    return ""

if sys.platform == "darwin":
    EMOJI_FONT = "Apple Color Emoji"
elif sys.platform == "win32":
    EMOJI_FONT = "Segoe UI Emoji"
else:
    EMOJI_FONT = "Noto Color Emoji"

class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()
        self.city_label = QLabel("Enter city name: ", self)
        self.city_input = QLineEdit(self)
        self.get_weather_button = QPushButton("Get Weather", self)
        self.temperature_label = QLabel("70 C", self)
        self.emoji_label = QLabel('☀', self)
        self.description_label = QLabel("Sunny", self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Weather App")

        vbox = QVBoxLayout()

        vbox.addWidget(self.city_label)
        vbox.addWidget(self.city_input)
        vbox.addWidget(self.get_weather_button)
        vbox.addWidget(self.temperature_label)
        vbox.addWidget(self.emoji_label)
        vbox.addWidget(self.description_label)

        self.setLayout(vbox)

        self.city_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.city_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.temperature_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.emoji_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.city_label.setObjectName("city_label")
        self.city_input.setObjectName("city_input")
        self.get_weather_button.setObjectName("get_weather_button")
        self.temperature_label.setObjectName("temperature_label")
        self.emoji_label.setObjectName("emoji_label")
        self.description_label.setObjectName("description_label")

        self.setStyleSheet("""
            QLabel{
                font-family: arial;
            }
            QLabel#city_label{
                font-size: 40px;
                font-style: italic;
            }
            QLineEdit#city_input{
                font-size: 40px;
                padding: 8px;
            }
            QPushButton#get_weather_button{
                font-size: 30px;
                font-weight: bold;
            }    
            QLabel#temperature_label{
                 font-size: 75px;
            }
            QLabel#emoji_label{
                 font-size: 100px;
                 font-family: "%s";
            }
            QLabel#description_label{
                 font-size: 50px;
            }
        """ % EMOJI_FONT)

        self.get_weather_button.clicked.connect(self.get_weather)

    def get_weather(self):

        api_key = load_api_key()
        if not api_key:
            self.display_error("Missing API key:\nSet OPENWEATHER_API_KEY in a .env file")
            return

        city = self.city_input.text()
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if data["cod"] == 200:
                self.display_weather(data)

        except requests.exceptions.HTTPError as http_error:
            match response.status_code:
                case 400:
                    self.display_error("Bad request:\nPlease check your input")
                case 401:
                    self.display_error("Unauthorized:\nInvalid API key")
                case 403:
                    self.display_error("Forbidden:\nAccess is denied")
                case 404:
                    self.display_error("Not found:\nCity not found")
                case 500:
                    self.display_error("Internal server error:\nPlease try again later")
                case 501:
                    self.display_error("Not implemented:\nThe server does not support this request")
                case _:
                    self.display_error(f"HTTP error:\n{http_error}")

        except requests.exceptions.ConnectionError:
            self.display_error("Connection error:\nCheck your internet connection")
        except requests.exceptions.Timeout:
            self.display_error("Timeout error:\nThe request timed out")
        except requests.exceptions.TooManyRedirects:
            self.display_error("Too many redirects:\nCheck the URL")
        except requests.exceptions.RequestException as req_error:
            self.display_error(f"Request Error:\n{req_error}")


    def display_error(self, message):
        self.temperature_label.setStyleSheet("font-size: 30px;")
        self.temperature_label.setText(message)
        self.emoji_label.clear()
        self.description_label.clear()

    def display_weather(self, data):
        self.temperature_label.setStyleSheet("font-size: 75px;")
        temp_k = data["main"]["temp"]
        temp_c = temp_k - 273.15

        weather = data["weather"][0]["description"]

        weather_id = data["weather"][0]["id"]

        self.temperature_label.setText(f"{temp_c:.0f}°C")
        self.emoji_label.setText(self.get_weather_emoji(weather_id))
        self.description_label.setText(f"{weather}")

    @staticmethod
    def get_weather_emoji(weather_id):
        if 200 <= weather_id <= 232:
            return "⛈"
        elif 300 <= weather_id <= 321:
            return "⛅︎"
        elif 500 <= weather_id <= 531:
            return "🌧️"
        elif 600 <= weather_id <= 622:
            return "❅"
        elif 701 <= weather_id <= 741:
            return "🌫️"
        elif weather_id == 762:
            return "🌋"
        elif weather_id == 771:
            return "💨"
        elif weather_id == 781:
            return "💨"
        elif weather_id == 800:
            return "☀"
        elif 801 <= weather_id <= 804:
            return "☁️"
        else:
            return ""


if __name__ == '__main__':
    app = QApplication(sys.argv)
    weather_app = WeatherApp()
    weather_app.show()
    sys.exit(app.exec())

