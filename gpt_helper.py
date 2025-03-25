import os
import sys
import json
import argparse
import hashlib
import shlex
import time
import subprocess
import platform
import fnmatch
import tkinter as tk


class GPTAssist:
    def __init__(self):
        self.project_name = ""
        self.context = {
            "url": [],
            "dir": [],
            "dir_ignore": [],
            "hashes": {},
            "allowed_extensions": {"*": 0}
        }

        self.allowed_exts = self.context["allowed_extensions"]

    def copy_to_clipboard(self, data):
        """
        Copy a string to the system clipboard using only built‑in modules.
        Works cross‑platform (Windows, macOS, Linux).
        """

        try:
            root = tk.Tk()
            root.withdraw()  # hide the main window
            root.clipboard_clear()  # clear current clipboard contents
            root.clipboard_append(data)  # append new text
            root.update()  # now it stays on the clipboard after the window closes
            root.destroy()
            print("Data successfully copied to clipboard.")
        except Exception as e:
            print(f"Failed to copy to clipboard: {e}")

    def print_status(self):
        print(f"Project Name : {self.project_name}")

        prefix = "-" * 2
        prefix2 = prefix * 2
        print("Dirs:")
        print(prefix, "Allowed paths")
        for d in self.context["dir"]:
            print(prefix2, d)
        print(prefix, "Restricted paths")
        for d in self.context["dir_ignore"]:
            print(prefix2, d)
        print("Urls:")
        for u in self.context["url"]:
            print(prefix, u)
        print("Allowed Extensions:")
        print(prefix, list(self.allowed_exts.keys()))

    def add_extension(self, extension=None):
        if not extension:
            extension = input(f"Enter extension to add to allowed list:({list(self.allowed_exts.keys())}): ").strip()
        if extension not in self.context["allowed_extensions"]:
            self.context["allowed_extensions"][extension] = 0
            self.allowed_exts = self.context["allowed_extensions"]

            print(f"Added extension '{extension}' to allowed list.")
        else:
            print(f"Extension '{extension}' is already in the allowed list.")

    def remove_extension(self, extension=None):
        if not extension:
            extension = input(f"Enter Extension to remove from allowed list:({list(self.allowed_exts.keys())}): ").strip()
        if extension in self.context["allowed_extensions"]:
            del self.context["allowed_extensions"][extension]
            self.allowed_exts = self.context["allowed_extensions"]
            print(f"Removed extension '{extension}' from allowed list.")
        else:
            print(f"Extension '{extension}' not found in allowed list.")


    def add_dir(self, dir_path=None):
        if not dir_path:
            dir_path = input("Enter directory to add to allowed list: ").strip()
        if dir_path not in self.context["dir"]:
            self.context["dir"].append(dir_path)
            print(f"Added directory '{dir_path}' to allowed list.")
        else:
            print(f"Directory '{dir_path}' is already in the allowed list.")

    def remove_dir(self, dir_path=None):
        if not dir_path:
            dir_path = input("Enter directory to remove from allowed list: ").strip()
        if dir_path in self.context["dir"]:
            self.context["dir"].remove(dir_path)
            print(f"Removed directory '{dir_path}' from allowed list.")
        else:
            print(f"Directory '{dir_path}' not found in allowed list.")

    def add_ignore_dir(self, dir_path=None):
        if not dir_path:
            dir_path = input("Enter directory to add to ignore list: ").strip()
        if dir_path not in self.context["dir_ignore"]:
            self.context["dir_ignore"].append(dir_path)
            print(f"Added directory '{dir_path}' to ignore list.")
        else:
            print(f"Directory '{dir_path}' is already in the ignore list.")

    def remove_ignore_dir(self, dir_path=None):
        if not dir_path:
            dir_path = input("Enter directory to remove from ignore list: ").strip()
        if dir_path in self.context["dir_ignore"]:
            self.context["dir_ignore"].remove(dir_path)
            print(f"Removed directory '{dir_path}' from ignore list.")
        else:
            print(f"Directory '{dir_path}' not found in ignore list.")

    def add_url(self, url=None):
        if not url:
            url = input("Enter URL to add: ").strip()
        if url not in self.context["url"]:
            self.context["url"].append(url)
            print(f"Added URL '{url}'.")
        else:
            print(f"URL '{url}' is already in the list.")

    def remove_url(self, url=None):
        if not url:
            url = input("Enter URL to remove: ").strip()
        if url in self.context["url"]:
            self.context["url"].remove(url)
            print(f"Removed URL '{url}'.")
        else:
            print(f"URL '{url}' not found in the list.")

    def print_dir_structure(self):
        """Print a tree-like structure for each allowed directory."""
        for directory in self.context["dir"]:
            print(f"\nDirectory structure for {directory}:")
            self._print_tree(directory, prefix="")

    def should_ignore(self, path):
        """
        Return True if the given relative path matches any ignore pattern.
        """
        for pattern in self.context["dir_ignore"]:
            if fnmatch.fnmatch(path, pattern):
                return True
        return False

    def _print_tree(self, directory, prefix=""):
        """
        Recursively prints a tree view of the directory.
        If an entry's relative path (from the current working directory) matches an ignore pattern,
        that entry (and its children) is skipped.
        """
        if prefix == "":
            print(os.path.basename(directory) + "/")
        try:
            entries = sorted(os.listdir(directory))
        except Exception as e:
            print(prefix + "Error accessing directory:", e)
            return
        for i, entry in enumerate(entries):
            full_path = os.path.join(directory, entry)
            rel_path = os.path.relpath(full_path, os.getcwd())
            # Skip if the path should be ignored.
            if self.should_ignore(rel_path):
                continue
            connector = "└── " if i == len(entries) - 1 else "├── "
            if os.path.isdir(full_path):
                print(prefix + connector + entry + "/")
                new_prefix = prefix + ("    " if i == len(entries) - 1 else "│   ")
                self._print_tree(full_path, new_prefix)
            else:
                print(prefix + connector + entry)

    def print_all(self):
        """
        Print the directory structure and file contents for all allowed directories,
        skipping directories that match ignore patterns.
        Only files with allowed extensions are printed.
        The file contents are wrapped in triple backticks.
        """
        allowed_exts = self.allowed_exts  # {".html", ".xml", ".csv", ".json", ".txt", ".sh", ".h", ".c", ".py"}
        for directory in self.context["dir"]:
            print(f"\n--- Scanning directory: {directory} ---")
            for root, dirs, files in os.walk(directory):
                # Compute the relative path from the current working directory.
                rel_root = os.path.relpath(root, os.getcwd())
                if self.should_ignore(rel_root):
                    continue
                print(f"\nDirectory: {root}")
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if ext not in allowed_exts or "*" not in allowed_exts or ".*" not in allowed_exts:
                        continue
                    file_path = os.path.join(root, file)
                    print(f"\n--- {file_path} ---")
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        # Wrap content in triple backticks for Markdown formatting.
                        print("```")
                        print(content)
                        print("```")
                    except Exception as e:
                        print(f"Error reading file {file_path}: {e}")
                    print(f"--- End of {file_path} ---")

    def read_file_contents(self):
        allowed_exts = self.allowed_exts

        results = []
        for directory in self.context["dir"]:
            for root, dirs, files in os.walk(directory):
                # Compute the relative path from the current working directory.
                rel_root = os.path.relpath(root, os.getcwd())
                # Skip this directory if it matches any ignore pattern.
                if self.should_ignore(rel_root):
                    continue
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if ext not in allowed_exts and "*" not in allowed_exts and ".*" not in allowed_exts:
                        continue
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        wrapped_content = "```\n" + content + "\n```"
                        rel_file_path = os.path.relpath(file_path, os.getcwd())
                        results.append((rel_file_path, wrapped_content))
                    except Exception as e:
                        continue
        return results

    def read_directory_contents(self):
        """
        Create a string of all possible file directories and return that string.
        It is similar to the output of the print_dir_structure command.
        """
        result_lines = []
        for directory in self.context["dir"]:
            result_lines.append(f"Directory structure for {directory}:")
            result_lines.extend(self._get_tree(directory, prefix=""))
        return "\n".join(result_lines)

    def _get_tree(self, directory, prefix=""):
        """
        Recursively collects a tree view of the directory as a list of strings.
        Entries whose relative path matches an ignore pattern are skipped.
        """
        lines = []
        # Print the root directory name only once at the top.
        if prefix == "":
            lines.append(os.path.basename(directory) + "/")
        try:
            entries = sorted(os.listdir(directory))
        except Exception as e:
            lines.append(prefix + "Error accessing directory: " + str(e))
            return lines
        for i, entry in enumerate(entries):
            full_path = os.path.join(directory, entry)
            rel_path = os.path.relpath(full_path, os.getcwd())
            # Skip if this path should be ignored.
            if self.should_ignore(rel_path):
                continue
            connector = "└── " if i == len(entries) - 1 else "├── "
            if os.path.isdir(full_path):
                lines.append(prefix + connector + entry + "/")
                new_prefix = prefix + ("    " if i == len(entries) - 1 else "│   ")
                lines.extend(self._get_tree(full_path, new_prefix))
            else:
                lines.append(prefix + connector + entry)
        return lines

    def prompt_first(self, print_it=True, copy_it=False):
        filecontents = self.read_file_contents()
        dircontents = self.read_directory_contents()

        filecontents_string = ""
        for filetuple in filecontents:
            filecontents_string += f"\n### File: {filetuple[0]}\n"
            filecontents_string += f"""\n{filetuple[1]}\n"""

        urlcontents = "" if self.context['url'] == [] else "\n## URL Contents\n"
        index = 1
        for url in self.context['url']:
            urlcontents += f"- {index}. {url}\n"
            index += 1

        prompt = f""" # Project: {self.project_name}\n\n## Directory Structure\n\n{dircontents}\n\n## File Contents\n\n{filecontents_string}\n\n{urlcontents}\n\nPlease analyze the above project structure and file contents, and answer any queries regarding its functionality."""

        if print_it:
            print(prompt)
        if copy_it:
            self.copy_to_clipboard(prompt)

    def hash(self, ob):
        return hashlib.md5(ob.encode('utf-8')).hexdigest()

    def update_hashes(self):
        self.context["hashes"] = {}
        filecontents = self.read_file_contents()
        dircontents = self.read_directory_contents()

        h = self.hash(dircontents)
        if h not in self.context["hashes"]:
            self.context["hashes"][h] = 1

        for filetuple in filecontents:
            h = self.hash(filetuple[1])
            if h not in self.context["hashes"]:
                self.context["hashes"][h] = 1

        for url in self.context['url']:
            h = self.hash(url)
            if h not in self.context["hashes"]:
                self.context["hashes"][h] = 1

    def prompt_update(self, print_it=True, copy_it=False):
        filecontents = self.read_file_contents()
        dircontents = self.read_directory_contents()

        filecontents_string = ""
        for filetuple in filecontents:
            if self.hash(filetuple[1]) in self.context["hashes"]:
                continue
            filecontents_string += f"\n### Updated File: {filetuple[0]}\n"
            filecontents_string += f"""\n{filetuple[1]}\n"""

        urlcontents = "" if self.context['url'] == [] else "\n## Updated URL Contents\n"
        index = 1
        for url in self.context['url']:
            if self.hash(url) in self.context["hashes"]:
                continue
            urlcontents += f"- {index}. {url}\n"
            index += 1

        dircontent_section = f"""\n## Updated Directory Structure\n\n{dircontents}\n"""
        filecontent_section = f"""\n## Updated File Contents\n\n{filecontents_string}\n"""

        if self.hash(dircontents) in self.context["hashes"]:
            dircontent_section = ""

        prompt = f""" # Project: {self.project_name}\n{dircontent_section}{filecontent_section}\n{urlcontents}\n\nPlease analyze the above updated project structure and file contents, and answer any queries regarding its functionality."""

        if print_it:
            print(prompt)
        if copy_it:
            self.copy_to_clipboard(prompt)

    def save(self, path=None):
        if not path:
            path = input("Enter path to save the context (e.g., context.json): ").strip()
        data = {
            "project_name": self.project_name,
            "context": self.context
        }
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            print(f"Context successfully saved to {path}.")
        except Exception as e:
            print(f"Error saving context: {e}")

    def load(self, path=None):
        if not path:
            path = input("Enter path to load the context (e.g., context.json): ").strip()
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.project_name = data.get("project_name", "")
            self.context = data.get("context", self.context)
            self.allowed_exts = self.context["allowed_extensions"]
            print(f"Context successfully loaded from {path}.")
        except Exception as e:
            print(f"Error loading context: {e}")


class Command:
    def __init__(self, command="", required_commands=None, optional_commands=None, inputs=None, help_message="",
                 ):
        if inputs is None:
            inputs = ""
        if optional_commands is None:
            optional_commands = []
        if required_commands is None:
            required_commands = []

        self.command = command

        self.command_without_hyphen = command.lower().lstrip('-')

        self.required_commands = required_commands
        self.optional_commands = optional_commands
        self.help_message = help_message
        self.inputs = inputs

    def generate_str(self):
        ret_str = []
        ret_str.append(f" {self.command} ")
        if self.inputs != "":
            ret_str.append(f"[{self.inputs}] ")

        ret_str.append(f": ")
        ret_str.append(f"{self.help_message}")

        if self.required_commands:
            required = ", ".join([cmd.command for cmd in self.required_commands])
            ret_str.append(f"\n\t[Require: {required}]")
        if self.optional_commands:
            optional = ", ".join([cmd.command for cmd in self.optional_commands])
            ret_str.append(f"\n\t[Optional: {optional}]")

        return ''.join(ret_str)

    def print_command(self):
        print(self.generate_str())

    def __repr__(self):
        return f"Command({self.command})"


help_comm = Command("-h", help_message="Prints help section")
project_name_comm = Command("-name", help_message="Project Name")
add_dir_comm = Command("-dir+", inputs="Directory", help_message="Adds directory to watch-list")
add_ignore_dir_comm = Command("-ignore+", inputs="Directory", help_message="Adds directory to ignore-list")
remove_dir_comm = Command("-dir-", inputs="Directory", help_message="Removes this directory from watch-list")
remove_ignore_dir_comm = Command("-ignore-", inputs="Directory", help_message="Removes this directory from ignore-list")
add_url_comm = Command("-url+", inputs="Url", help_message="Removes given url from watch-list")
remove_url_comm = Command("-url-", inputs="Url", help_message="Removes given url from watch-list")
add_extension_comm = Command("-extension+", help_message="Removes given extension from allowed-list")
remove_extension_comm = Command("-extension-", help_message="Removes given extension from allowed-list")
print_all_comm = Command("-print", help_message="Prints directory structure and contents of all the files")
print_dir_structure_comm = Command("-printdir", help_message="Prints directory structure")
status_comm = Command("-status", help_message="Prints current status")
prompt_first_copy_comm = Command("-prompt-first-copy", help_message="Copys the first prompt to clipboard")
prompt_update_copy_comm = Command("-prompt-copy", help_message="Copys the updated prompt to clipboard")
prompt_first_comm = Command("-prompt-first", help_message="Prints and copys the first prompt")
prompt_update_comm = Command("-prompt", help_message="Prints and copys the updated prompt")
update_comm = Command("-update", help_message="Updates the hashes")
save_comm = Command("-save", help_message="Saves the context")
load_comm = Command("-load", help_message="Loads the context")


class Command_Control:
    def __init__(self, header="", logfile=None):
        self.commands = []
        self.header = header
        if logfile:
            self.logfilename = logfile
            self.logging = True
            with open(self.logfilename, "w") as file:
                file.write("Time | Valid/Invalid | Command(if Valid) | InputParameters\n")
        else:
            self.logfilename = None
            self.logging = False

    def add_command(self, *commands):
        for cmd in commands:
            self.commands.append(cmd)

    def print_all_commands(self):
        print(f"---------------------- {self.header} ------------------------")
        for cmd in self.commands:
            cmd.print_command()
        print(f"---------------------- {self.header} ------------------------")

    def parse_command(self, input_command):
        tokens = shlex.split(input_command)
        dictionary_commands = {}
        key = None
        for token in tokens:
            if token.startswith("-"):
                key = token.lstrip("-")
                dictionary_commands[key] = None
            else:
                if key:
                    dictionary_commands[key] = token
        return dictionary_commands

    def validate_action(self, action):
        for cmd in self.commands:
            if cmd.command_without_hyphen in action:
                # Check for required commands
                missing_required = False
                for req_cmd in cmd.required_commands:
                    if req_cmd.command_without_hyphen not in action or not action[req_cmd.command_without_hyphen]:
                        missing_required = True
                        break
                if missing_required:
                    print(f"Incomplete command '{cmd.command}'. Enter -h for help.")
                    return False, action, None
                return True, action, cmd
        # print("Unknown (or incomplete) command entered. Enter -h for help.")
        return False, action, None

    def resolve_cmd(self, terminal_cmd):
        action_dict = self.parse_command(terminal_cmd)
        is_valid, action_dict, action_cmd = self.validate_action(action_dict)
        if self.logging:
            self.log(is_valid, action_dict, action_cmd)
        if is_valid:
            return action_dict, action_cmd
        else:
            return action_dict, None

    def log(self, is_valid, param_dict, param_cmd):
        if not self.logfilename:
            return
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        with open(self.logfilename, "a") as file:
            if not is_valid:
                file.write(f"{timestamp} -> Invalid | {param_dict}\n")
            else:
                file.write(f"{timestamp} -> Valid | {param_cmd.command_without_hyphen} | {param_dict}\n")

    def get_command_names_lstriped(self):
        return [cmd.command_without_hyphen for cmd in self.commands]

    def get_command(self, command_name):
        return [cmd for cmd in self.commands if cmd.command_without_hyphen == command_name][0]

    def is_parameters_valid(self, command_dict):
        for key in command_dict.keys():
            if command_dict[key] is None and self.get_command(key).inputs != "":
                return False
        return True


class Terminal:
    def __init__(self, sudo_password=None, command_control_object=None):
        if command_control_object is None:
            self.CommandControl = Command_Control()
        else:
            self.CommandControl = command_control_object

        self.is_windows = platform.system().lower() == "windows"
        self.is_linux = platform.system().lower() == "linux"
        self.sudo_password = sudo_password

    def run_command(self, command):
        """
        Execute a shell command.
        :param command: Command string to execute.
        :return: Tuple containing (output, success_flag)
        """
        if self.is_linux:
            try:
                if command.startswith("sudo") and self.sudo_password:
                    # Securely provide the sudo password via stdin
                    process = subprocess.Popen(
                        ['sudo', '-S'] + shlex.split(command[5:]),
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    stdout, stderr = process.communicate(input=self.sudo_password + '\n')
                else:
                    process = subprocess.Popen(
                        shlex.split(command),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    stdout, stderr = process.communicate()

                if process.returncode == 0:
                    return stdout, True
                else:
                    return stderr, False

            except Exception as e:
                return f"Error running command: {str(e)}", False

        elif self.is_windows:
            try:
                process = subprocess.Popen(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                stdout, stderr = process.communicate()

                if process.returncode == 0:
                    return stdout, True
                else:
                    return stderr, False
            except Exception as e:
                return f"Error running command: {str(e)}", False
        else:
            return "Unsupported OS", False

    def interactive_shell(self):
        """
        Launch an interactive shell interface.
        """
        print("Starting Terminal Shell. Type 'exit' to quit.")
        print("Path where these commands will get execured : {}")
        while True:
            try:
                command_input = input("> ").strip()
                if command_input.lower() in ["exit", "quit"]:
                    print("Exiting shell.")
                    break

                action_dict, action_cmd = self.CommandControl.resolve_cmd(command_input)
                print(action_cmd, self.CommandControl.get_command_names_lstriped())
                if action_cmd is not None and \
                        action_cmd.command_without_hyphen in self.CommandControl.get_command_names_lstriped():
                    print(action_dict)
                else:
                    output, success = self.run_command(command_input)
                    print(output)


            except KeyboardInterrupt:
                print("\nExiting shell.")
                break
            except EOFError:
                print("\nExiting shell.")
                break

    # # Example usage
    # if __name__ == "__main__":
    #     sudo_password = input("Enter your sudo password (leave blank if not required): ")
    #     terminal = Terminal(sudo_password if sudo_password.strip() else None)
    #     terminal.interactive_shell()
    #


gpt = GPTAssist()

GPT_Assist_Cmd_Prompt = Command_Control("GPT Assist")

GPT_Assist_Cmd_Prompt.add_command(help_comm, project_name_comm, add_dir_comm, add_ignore_dir_comm, add_url_comm,
                                  add_extension_comm,status_comm, update_comm, remove_extension_comm,
                                  remove_dir_comm, remove_ignore_dir_comm, remove_url_comm, print_all_comm,
                                  print_dir_structure_comm,
                                  prompt_first_copy_comm, prompt_update_copy_comm, prompt_first_comm,
                                  prompt_update_comm, save_comm, load_comm)

GPT_Assist_Cmd_Prompt.print_all_commands()

default_ignore_list = [r"*venu*",r"*venv*", r"*.git*", r"*.idea*", r"*.jpg", r"*.bmp", r"*.png", r"*.jpeg",
                       r"*.pdf", r"*LICENSE", r"*.zip"]


[gpt.add_ignore_dir(dir_path=a) for a in default_ignore_list]
starttime_time = time.time()

while True:
    bookmark_time = time.time()
    input_command = str(input(f"({str(int(time.time() - starttime_time)).zfill(3)} sec) > "))
    resolved_cmd = GPT_Assist_Cmd_Prompt.resolve_cmd("-" + input_command)
    # print(resolved_cmd)
    cmd = resolved_cmd[1]
    # print(type(cmd))

    if resolved_cmd[1] is None:
        print("Invalid Command")
    else:
        if GPT_Assist_Cmd_Prompt.is_parameters_valid(resolved_cmd[0]) or True:
            # print("Valid Command")
            if cmd.command_without_hyphen == help_comm.command_without_hyphen:
                GPT_Assist_Cmd_Prompt.print_all_commands()

            if cmd.command_without_hyphen == status_comm.command_without_hyphen:
                gpt.print_status()

            if cmd.command_without_hyphen == add_dir_comm.command_without_hyphen:
                gpt.add_dir()
            if cmd.command_without_hyphen == remove_dir_comm.command_without_hyphen:
                gpt.remove_dir()
            if cmd.command_without_hyphen == add_ignore_dir_comm.command_without_hyphen:
                gpt.add_ignore_dir()
            if cmd.command_without_hyphen == remove_ignore_dir_comm.command_without_hyphen:
                gpt.remove_ignore_dir()
            if cmd.command_without_hyphen == add_url_comm.command_without_hyphen:
                gpt.add_url()
            if cmd.command_without_hyphen == remove_url_comm.command_without_hyphen:
                gpt.remove_url()
            if cmd.command_without_hyphen == print_dir_structure_comm.command_without_hyphen:
                gpt.print_dir_structure()
            if cmd.command_without_hyphen == print_all_comm.command_without_hyphen:
                gpt.print_all()
            if cmd.command_without_hyphen == prompt_first_comm.command_without_hyphen:
                gpt.prompt_first()
            if cmd.command_without_hyphen == update_comm.command_without_hyphen:
                gpt.update_hashes()
            if cmd.command_without_hyphen == prompt_update_comm.command_without_hyphen:
                gpt.prompt_update()
            if cmd.command_without_hyphen == project_name_comm.command_without_hyphen:
                gpt.project_name = str(input("Enter the Project Name : "))
            if cmd.command_without_hyphen == prompt_first_copy_comm.command_without_hyphen:
                gpt.prompt_first(print_it=False, copy_it=True)
            if cmd.command_without_hyphen == prompt_update_copy_comm.command_without_hyphen:
                gpt.prompt_update(print_it=False, copy_it=True)
            if cmd.command_without_hyphen == save_comm.command_without_hyphen:
                gpt.save()
            if cmd.command_without_hyphen == load_comm.command_without_hyphen:
                gpt.load()
            if cmd.command_without_hyphen == add_extension_comm.command_without_hyphen:
                gpt.add_extension()
            if cmd.command_without_hyphen == remove_extension_comm.command_without_hyphen:
                gpt.remove_extension()



        else:
            print("Invalid Command Usage")
#
#
