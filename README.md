# 📝 Macky's Smart Notebook

Macky's Smart Notebook is a feature-rich, offline desktop note-taking application developed using Python, Tkinter, and SQLite3. Designed for students, professionals, and writers, it provides a distraction-free environment to take notes, track them, and gain insights with a visual dashboard.

Built with modular components and a clean architecture, the application includes a secure login system, note editor, database manager, and interactive analytics—all in one offline package.

---

## 🌟 Features

✅ User Authentication

* Sign up/login system with local credential storage
* Password-protected access

✅ Note Management

* Create, edit, view, and delete notes
* Store and retrieve notes from local database (SQLite)
* Simple and clean editor UI with text formatting options (planned)

✅ Data Persistence

* SQLite3 database (notes.db) for fast local storage
* Modular db\_manager.py for CRUD operations

✅ Dashboard & Analytics

* See total number of notes created
* Visual summary of notes created per user
* Simple GUI-based data visualization using Tkinter canvas (future: matplotlib)

✅ Modular Codebase

* Easy to extend and maintain
* Components split across auth.py, editor.py, dashboard.py, db\_manager.py, and main.py

✅ Cross-Platform Support

* Built with Python and Tkinter for compatibility across Windows, Linux, and macOS

---

## 🛠️ Tech Stack

* 💻 Language: Python 3.x
* 🖼️ GUI Framework: Tkinter
* 🗃️ Database: SQLite3 (file-based)
* 📊 Dashboard (basic Tkinter canvas UI)
* 🔐 Authentication: Custom login/signup with hashed credentials (planned)

---

## 🗂️ Project Structure

```
Macky-s-Smart-Notebook/
│
├── auth.py             # Handles user login and signup logic
├── dashboard.py        # Visual dashboard for stats and summaries
├── db_manager.py       # All SQLite3 database functions and helpers
├── editor.py           # Note editor window and editing functions
├── main.py             # Main entry point for launching the app
├── notes.db            # SQLite database storing users and notes
├── requirements.txt    # Python package dependencies
└── README.md           # This file
```

---

## 🚀 Getting Started

Follow these steps to run the application locally.

### 1. Clone the Repository

```bash
git clone https://github.com/pankajkr-143/Macky-s-Smart-Notebook.git
cd Macky-s-Smart-Notebook
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

This includes:

* tkinter (standard with Python on most systems)
* sqlite3 (standard with Python)
* Optional: matplotlib (if integrated for advanced analytics later)

### 3. Run the Application

```bash
python main.py
```

---

## 🔐 Authentication System

* When the application starts, you'll be prompted to log in or sign up.
* User credentials are stored in the local SQLite database (future version may include hashed storage).
* After login, users are redirected to the main note-taking interface.

---

## 📊 Dashboard Module

Access the dashboard from the menu to see:

* Total number of notes
* Notes created per session or user
* Placeholder for future charts/visuals (bar chart, pie chart, etc.)

---

## 🧠 Planned Enhancements

* Dark/Light Theme Toggle
* Markdown support in editor
* Export notes to .txt, .md, and PDF
* Full-text search across all notes
* Calendar view for journal-style entries
* Category/tag support for notes
* Cloud sync using Google Drive or Dropbox APIs
* Text-to-speech using pyttsx3
* AI summarizer for long notes using NLP

---

## 🙋‍♂️ Contributing

We welcome all contributors! Whether it's improving the UI, adding new features, or fixing bugs:

1. Fork this repository
2. Create a feature branch (git checkout -b feature-name)
3. Commit your changes (git commit -m "Add new feature")
4. Push to your branch (git push origin feature-name)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License. See the LICENSE file for more information.

---

## 📎 Contact

Developed by Pankaj Kumar
🔗 GitHub: [https://github.com/pankajkr-143/Macky-s-Smart-Notebook](https://github.com/pankajkr-143/Macky-s-Smart-Notebook)
