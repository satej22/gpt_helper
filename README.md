# 🚀 GPT Helper

**GPT Helper** is a versatile, cross-platform command-line tool written in Python that helps you **analyze project directories, manage file contents, handle URLs**, and generate prompts for LLMs like ChatGPT — all from an interactive shell.

It supports clipboard integration, smart file filtering, and change detection to streamline your workflow.

---

## 🛠 Requirements

- Python **3.x**
- Tkinter (comes pre-installed with most Python distributions)

---

## 📦 Installation

This is a standalone script — no installation needed! Just download the file and run it:

```bash
python gpthelper.py
```

## 💡 Usage
After launching, you'll be greeted with an interactive prompt. Type any of the following commands:
Command	Description
-h	Show help and list all available commands
-name	Set project name
-dir+	Add a directory to the watch list
-dir-	Remove a directory from the watch list
-ignore+	Add a directory pattern to ignore list
-ignore-	Remove a directory pattern from ignore list
-url+	Add a URL
-url-	Remove a URL
-extension+	Add allowed file extension
-extension-	Remove allowed file extension
-print	Show directory structure + file contents
-printdir	Show directory structure only
-prompt-first	Print first prompt with all data
-prompt-first-copy	Copy the first prompt to clipboard
-prompt	Print updated prompt (only new/changed)
-prompt-copy	Copy updated prompt to clipboard
-update	Update hashes for file/directory changes
-save	Save project context to .json
-load	Load project context from .json
☝️ If no argument is passed to a command, the program will interactively ask you for input.
You can ignore prefix  **-** (dash) while giving command. 

## ✨ Features

✅ Clipboard Integration
Copy generated prompts to your system clipboard using tkinter.

📂 Directory & File Management
Add/remove directories to monitor
Tree-like structure output
Ignore directories/patterns

📄 File Content Display
View contents of files with allowed extensions
Markdown-wrapped output for LLM compatibility

🌐 URL Support
Track URLs related to your project
Include them in prompt generation

🔄 Change Detection
Smart hashing to detect file/directory changes
-prompt only shows what's new

## 📃 License
This project is licensed under the MIT License. See the LICENSE file for full details.

## 🤝 Contributing
Contributions and suggestions are welcome!
Feel free to open an issue or submit a pull request 💡


