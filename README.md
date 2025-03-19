# 🍾 WhiskeyReleasePageMon

A powerful Python-based scraper that fetches the current available products and stock data from the **REDACTED** Whiskey Release page. The currently available product information is then stored to a local SQLite database and compared agaisnt for updates each time the program executes. This project supports proxy rotation, logging, and API request retries to ensure reliable data retrieval.

## 🚀 Features

- ✅ **Proxy Support** – Loads and validates proxies from a file before use
- ✅ **TLS Client Integration** – Uses `tls_client` for enhanced request security
- ✅ **Robust Logging** – Logs events to both console and a rotating log file
- ✅ **Environment Configuration** – `.env` file support for API URLs and proxy settings
- ✅ **Automatic Proxy Cleaning** – Removes dead proxies to improve performance
- ✅ **Error Handling & Retries** – Ensures smooth API calls with automatic retries  

## 📦 Installation

```sh
# 1️⃣ Clone the repository
git clone https://github.com/yourusername/WhiskeyReleasePageMon.git
cd WhiskeyReleasePageMon

# 2️⃣ Create a virtual environment (optional but recommended)
python -m venv venv
# If on Linux
source venv/bin/activate
# On Windows use
venv\Scripts\activate

# 3️⃣ Install dependencies
pip install -r requirements.txt

# 4️⃣ Create a .env file and configure your environment variables


## 🔧 Usage
# Run the program
python main.py

## 🛡️ Proxy Handling
Proxies are loaded from the file specified in PROXY_FILE
Dead proxies are automatically removed before each run

## 📝 Logging
Logs are saved to the path defined in LOG_FILE_PATH
Both console and file logging are enabled with color-coded output

## 🛠 Configuration
Modify .env or directly edit main.py to customize:

## 🌐 API Endpoints
Proxy rotation settings
Logging behavior

## 🏗 Future Enhancements
🔄 TBD

## 📜 License
This project is licensed under the MIT License, meaning you can use, modify, and distribute it, even for commercial purposes.

## 👨‍💻 Contributing
Want to contribute? Feel free to fork the repo and submit a pull request! 🚀
