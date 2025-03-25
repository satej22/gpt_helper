#GPT Helper
##GPT Helper is a command-line utility written in Python that assists in managing and analyzing project directories, file contents, and URLs. It provides an interactive shell where you can add or remove directories to watch, set up ignore patterns, and quickly view or copy project details to the clipboard. The tool is designed to work cross-platform (Windows, macOS, Linux).

##Features
###Clipboard Operations:
Copy text to the system clipboard using tkinter.

###Directory and File Management:

Add and remove directories to monitor.

Maintain an ignore list for directories or file patterns.

Display the directory structure in a tree-like format.

###File Content Display:

Read and display file contents with allowed extensions.

Format file content output in Markdown for clarity.

###URL Management:
Add and remove URLs associated with your project.

###Change Detection:
Compute hash values for directories and files to detect updates.

###Command Parsing & Logging:
A custom command parser validates and logs user commands for interactive use.

#Requirements
Python 3.x

Tkinter (included with Python on Windows and macOS; on Linux you may need to install it separately)

#Installation
This is a standalone Python script. Simply download the file (gpt_helper.py) and run it using Python:

```python gpt_helper.py
```
Usage
Upon running the script, you will be presented with an interactive prompt where you can type commands. Some available commands include:

-h : Display help and list all available commands.

-name : Set the project name.

-dir+ [Directory] : Add a directory to the watch list.

-dir- [Directory] : Remove a directory from the watch list.

-ignore+ [Directory] : Add a directory to the ignore list.

-ignore- [Directory] : Remove a directory from the ignore list.

-url+ [Url] : Add a URL to the project.

-url- [Url] : Remove a URL from the project.

-extension+ : Add a file extension to the allowed list.

-extension- : Remove a file extension from the allowed list.

-print : Print the full directory structure and file contents.

-printdir : Print only the directory structure.

-prompt-first : Display the initial project prompt (directory structure and file contents).

-prompt-first-copy : Copy the initial prompt to the clipboard.

-prompt : Display the updated project prompt.

-prompt-copy : Copy the updated prompt to the clipboard.

-update : Update hash values for change detection.

-save : Save the current project context to a file.

-load : Load the project context from a file.

Each command may prompt for additional input.

###License
This project is licensed under the MIT License. See the LICENSE file for details.

###Contributing
Contributions are welcome! Feel free to open issues or submit pull requests with suggestions or improvements.

###Contact
For any questions or suggestions, please contact satejbhave2002@gmail.com
