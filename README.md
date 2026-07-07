# 🛡️ StegShield

**StegShield** is a web-based Digital Forensics and Steganography tool. It allows you to secretly hide text messages inside of images using strong AES-256 encryption, while providing a modern, "cyber-security" themed interface.

It also comes with a forensics toolkit to analyze images, detect hidden payloads, and generate stylish PDF reports!

---

## ✨ What Can It Do?

1. **🔒 Hide Messages:** Type a secret message, set a password, and hide it inside any PNG image.
2. **🔓 Extract Messages:** Upload an encoded image, enter the password, and retrieve your hidden text.
3. **🔍 Analyze Images:** Upload any image to scan its metadata, check its file size, and see if it contains hidden data.
4. **📊 Generate PDF Reports:** Download a beautiful, cyber-themed PDF report of your image analysis, complete with SHA-256 hashes and the embedded image.
5. **🧮 Capacity Calculator:** See exactly how much space is left in an image as you type your secret message (with a live progress bar).

---

## 🚀 How to Run the Project

### 1. Prerequisites

Make sure you have Python installed on your computer.

### 2. Install Dependencies

Open your terminal or command prompt in the `StegShield` folder and run this command to install the required libraries:

```bash
pip install -r requirements.txt
```

### 3. Start the App

Start the web server by running:

```bash
python app.py
```

### 4. Open in Browser

Once the server is running, open your web browser and go to:
👉 **[http://127.0.0.1:5000/](http://127.0.0.1:5000/)**

---

## 📁 What's Inside?

- `app.py`: The main brain of the web application.
- `utils/`: The engine room! Contains the Python scripts for encryption (`crypto.py`), image hiding (`stego.py`), analysis (`analysis.py`), and PDFs (`report.py`).
- `templates/`: The HTML blueprints for all the different web pages.
- `static/`: The CSS and Javascript that give the app its sleek, dark cyber-look and animations.
