import os
import subprocess
import random
import time
import sys

CMD_FILE = "cmds.txt"

# ---------------- STATE ----------------
current_user = "user"
current_dir = "/home/user"

is_root = False
sudo_mode = False
sudo_last_time = 0
SUDO_TIMEOUT = 300

history = []
commands = {}
sudo_log = []

# ---------------- COLORS ----------------
RED_DARK = "\033[38;5;88m"
BLUE = "\033[34m"
GREEN = "\033[32m"
RESET = "\033[0m"

# ---------------- ERRORS ----------------
ERRORS = [
    "bash: {cmd}: command not found",
    "sh: {cmd}: not found",
    "{cmd}: command not found"
]

def err(cmd):
    print(random.choice(ERRORS).replace("{cmd}", cmd))

# ---------------- LOAD COMMANDS ----------------
def load_commands():
    global commands
    commands = {}

    if not os.path.exists(CMD_FILE):
        return

    with open(CMD_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if ">" in line:
                k, v = line.strip().split(">", 1)
                commands[k.strip()] = v.strip()

# ---------------- PROMPT ----------------
def format_path(path, user):
    home = f"/home/{user}"
    return "~" if path == home else path


def prompt():
    user = "root" if is_root else current_user
    symbol = "#" if is_root else "$"

    user_host = f"{RED_DARK}{user}㉿kali{RESET}"
    path = format_path(current_dir, current_user)

    branch = f" {GREEN}(main){RESET}" if "git" in commands else ""

    return f"-({user_host})-[{BLUE}{path}{RESET}]{branch}\n└─{symbol} "

# ---------------- LOGIN ----------------
def login():
    global current_user
    current_user = input("Username: ").strip() or "user"
    input("Password: ")

# ---------------- SUDO ----------------
def sudo_check():
    global is_root, sudo_mode, sudo_last_time

    if sudo_mode and time.time() - sudo_last_time < SUDO_TIMEOUT:
        is_root = True
        return

    input("[sudo] password: ")
    sudo_mode = True
    is_root = True
    sudo_last_time = time.time()

# ---------------- NORMALIZE ----------------
def normalize(cmd):
    parts = cmd.split()

    if parts and parts[0] == "sudo":
        return " ".join(parts[1:]), True

    return cmd, False

# ---------------- FS ----------------
def cd(path):
    global current_dir

    if not path:
        return

    if path == "..":
        if current_dir != "/":
            current_dir = "/".join(current_dir.rstrip("/").split("/")[:-1]) or "/"
        return

    current_dir = current_dir.rstrip("/") + "/" + path


def nano(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
    else:
        lines = []

    while True:
        print("\033c", end="")
        print(f"nano editing: {filename}\n")

        for i, l in enumerate(lines):
            print(f"{i}: {l}")

        cmd = input("> ")

        if cmd == "CTRL+X":
            break

        if cmd == "CTRL+S":
            with open(filename, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            continue

        if cmd.startswith("DEL "):
            try:
                lines.pop(int(cmd.split()[1]))
            except:
                pass
            continue

        if cmd.startswith("EDIT "):
            try:
                _, i, text = cmd.split(" ", 2)
                lines[int(i)] = text
            except:
                pass
            continue

        lines.append(cmd)

# ---------------- ADD CMD ----------------
def add_cmd():
    linux = input(": ").strip()
    windows = input(": ").strip()

    with open(CMD_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n{linux}>{windows}")

    load_commands()
    print("command added + live reload complete")

# ---------------- AUTOCOMPLETE (fake) ----------------
def autocomplete(cmd):
    matches = [c for c in commands.keys() if c.startswith(cmd)]
    return matches[0] if matches else cmd

# ---------------- RUNNER ----------------
def run(line):
    global is_root, sudo_last_time

    history.append(line)

    line, used_sudo = normalize(line)
    parts = line.split()

    if not parts:
        return True

    cmd = parts[0]
    args = parts[1:]

    # core commands
    if cmd == "exit":
        return False

    if cmd == "history":
        print("\n".join(history))
        return True

    if cmd == "reload":
        load_commands()
        print("reloaded")
        return True

    if cmd == "cd":
        cd(args[0] if args else "")
        return True

    if cmd == "nano":
        nano(args[0] if args else "file.txt")
        return True

    if cmd == "add" and args == ["cmd"]:
        add_cmd()
        return True

    if cmd == "sudo-log":
        print("\n".join(sudo_log))
        return True

    # sudo system
    if used_sudo:
        sudo_log.append(line)
        sudo_check()
        sudo_last_time = time.time()

    # command execution
    if cmd in commands:
        subprocess.run(commands[cmd] + " " + " ".join(args), shell=True)
    else:
        err(cmd)

    return True

# ---------------- MAIN ----------------
def main():
    os.makedirs("home", exist_ok=True)

    load_commands()
    login()

    while True:
        try:
            cmd = input(prompt()).strip()

            # fake autocomplete trigger
            if cmd.endswith("\t"):
                cmd = autocomplete(cmd.replace("\t", ""))

            if cmd:
                if not run(cmd):
                    break

        except KeyboardInterrupt:
            print()
            break


main()
