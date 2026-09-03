# Scamlex (ScamCheck)

> A comprehensive scam and phishing detection platform featuring a modern web application, a robust Python backend, and a real-time Chrome Extension.

## 📖 Project Purpose
Scamlex (ScamCheck) is designed to protect users from malicious websites, phishing attempts, and online scams. By utilizing a pattern-matching database and URL analysis algorithms, the system evaluates links and web content to determine their safety. Users can access this protection via a dedicated web scanner interface or seamlessly through a browser extension.

## ✨ Key Features
* **URL & Content Scanner:** A dedicated web interface (`scanner.tsx`) to manually input and analyze suspicious URLs.
* **Real-Time Browser Protection:** A Chrome Extension that allows users to quickly scan the active tab or check links on the fly.
* **Pattern-Based Detection:** Utilizes a custom backend detection engine (`detector.py` and `url_utils.py`) backed by an SQLite database (`scamcheck.db`) of known seed patterns.
* **Modern UI/UX:** Built with a highly responsive, accessible frontend using React, Tailwind CSS, and shadcn/ui components.
* **Dedicated Landing Page:** A polished introduction to the tool (`scamlex-landing.tsx`).

## 🛠️ Technologies & Frameworks Used

**Frontend**
* React (TypeScript)
* Vite (Build tool)
* Tailwind CSS (Styling)
* shadcn/ui (Component library)
* TanStack Router (Routing)
* Bun (Package manager & runtime)

**Backend**
* Python 3.x
* SQLite3 (Database)
* Custom Detection Logic (`detector.py`, `url_utils.py`)

**Browser Extension**
* HTML, CSS, JavaScript
* Chrome WebExtensions API (`manifest.json V3`)

## 📂 Project Architecture

```text
ScamCheck-Project-scamlex/
├── Backend/                    # Python API and core detection logic
│   ├── data/                   # Contains scamcheck.db and seed_patterns.py
│   ├── src/                    # Backend source code (app.py, main.py, detector.py)
│   └── tests/                  # Test cases (e.g., False_Negative_Test_Cases.txt)
├── Chrome Extension/           # Browser extension source files
│   ├── Icons/                  # Extension assets
│   ├── background.js           # Extension service worker
│   ├── content.js              # Content scripts for page interaction
│   ├── popup.html & popup.js   # Extension UI and logic
│   └── manifest.json           # Extension configuration
├── src/                        # Frontend source code
│   ├── components/             # Reusable UI components (shadcn/ui, scanner, landing)
│   ├── routes/                 # Frontend routing configuration
│   ├── lib/ & hooks/           # Utilities and custom React hooks
│   └── styles.css              # Global styles
├── package.json & bun.lock     # Frontend dependencies
├── vite.config.ts              # Vite bundler configuration
└── components.json             # shadcn/ui configuration

```

## ⚙️ System Requirements

* **Node.js** (v16+) or **Bun** (recommended, based on `bun.lock`)
* **Python** 3.8 or higher
* **Google Chrome** or a Chromium-based browser (for the extension)

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd ScamCheck-Project-scamlex

```

### 2. Backend Setup (Python)

1. Navigate to the backend directory:
```bash
cd Backend

```


2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

```


3. Initialize the database and seed patterns:
```bash
python data/seed_patterns.py

```


4. Start the backend server:
```bash
python src/main.py 
# or python src/app.py (depending on your entry point)

```



### 3. Frontend Setup (Web App)

1. Open a new terminal instance and navigate to the project root.
2. Install dependencies using Bun:
```bash
bun install

```


3. Start the Vite development server:
```bash
bun run dev

```


4. Open your browser and navigate to the local URL provided by Vite (usually `http://localhost:5173`).

### 4. Chrome Extension Setup

1. Open Google Chrome and navigate to `chrome://extensions/`.
2. Enable **"Developer mode"** in the top right corner.
3. Click **"Load unpacked"**.
4. Select the `Chrome Extension` folder located in the project root.
5. Pin the Scamlex extension icon to your browser toolbar.

## 💻 How to Use the Application

* **Web Scanner:** Navigate to the local frontend URL. Use the Landing Page to navigate to the Scanner, input a suspicious URL, and click scan. The app will communicate with the backend to analyze the link.
* **Chrome Extension:** Click the Scamlex icon in your Chrome toolbar while browsing a suspicious site. The popup will analyze the current page's URL and return a safety verdict.

## 🔌 API Endpoints (Backend)

*(Note: Refer to `Backend/src/app.py` for exact routing configurations)*

* The backend exposes RESTful endpoints (likely via Flask/FastAPI based on the `app.py` structure) that the frontend and extension consume to pass URLs to `detector.py` and retrieve JSON safety reports.

## 🖼️ Screenshots

*(Replace these placeholders with actual screenshots of your project)*

> **Placeholder: Web App Landing Page**
> `![Landing Page](docs/screenshots/landing.png)`

> **Placeholder: Scanner Interface in Action**
> `![Scanner](docs/screenshots/scanner.png)`

> **Placeholder: Chrome Extension Popup**
> `![Extension](docs/screenshots/extension.png)`

## 🚧 Known Limitations

* The detection relies on the patterns stored in `scamcheck.db`. Zero-day scams or URLs not matching existing criteria (`False_Negative_Test_Cases.txt`) may require manual verification.
* The backend server must be actively running locally for the frontend and extension to process scans.

## 🔮 Future Improvements

* Integration of machine learning models for predictive scam detection beyond static pattern matching.
* Cloud hosting deployment for the backend database to allow standalone use of the Chrome Extension without a local server.
* Community reporting feature to dynamically update `seed_patterns.py`.

## 🤝 Contribution Instructions

1. Fork the repository.
2. Create your feature branch: `git checkout -b feature/AmazingFeature`
3. Commit your changes: `git commit -m 'Add some AmazingFeature'`
4. Push to the branch: `git push origin feature/AmazingFeature`
5. Open a Pull Request.

## 📄 License

This project is open-source. Please refer to the `LICENSE` file in the repository for more details.

```

```
