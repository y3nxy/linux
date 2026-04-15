import os

CMD_FILE = "cmds.txt"
USER_FILE = "user.txt"

# -------------------------
# USER SYSTEM (DEFAULT SAFE)
# -------------------------
def get_user():
    if not os.path.exists(USER_FILE):
        return "user"

    with open(USER_FILE, "r", encoding="utf-8") as f:
        user = f.read().strip()

    return user if user else "user"


user = get_user()


# -------------------------
# LOAD COMMANDS (FAST DICT)
# -------------------------
def load_cmds():
    cmd_map = {}

    if not os.path.exists(CMD_FILE):
        open(CMD_FILE, "w").close()
        return cmd_map

    with open(CMD_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if "=" not in line:
                continue

            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip()

            if not k or not v:
                continue

            if k == v:
                continue

            cmd_map[k] = v

    return cmd_map


cmd_map = load_cmds()


# -------------------------
# TRANSLATOR
# -------------------------
def translate(cmd):
    if not cmd:
        return ""

    parts = cmd.strip().split()
    if not parts:
        return ""

    base = parts[0]
    args = " ".join(parts[1:])

    if base in cmd_map:
        return cmd_map[base] + (" " + args if args else "")

    return cmd


# -------------------------
# ADD CMD (SAFE + NO DUPES)
# -------------------------
def add_cmd():
    global cmd_map

    while True:
        name = input("Enter name: ").strip()

        if not name:
            print("invalid name")
            continue

        if name in cmd_map:
            print("alias already exists, pick a different name")
            continue

        actual = input("Enter actual command: ").strip()

        if not actual:
            print("invalid command")
            continue

        with open(CMD_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n{name}={actual}")

        cmd_map[name] = actual
        print("CMD is usable.")
        break


# -------------------------
# RENAME (IN MEMORY ONLY)
# -------------------------
def rename_user():
    global user

    new_user = input("Enter new username: ").strip()

    if not new_user:
        print("invalid username")
        return

    user = new_user
    print("username updated.")


# -------------------------
# PROMPT UI
# -------------------------
def prompt():
    u = user or "user"
    return f"┌──({u}㉿kali)-[~]\n└─$ "


# -------------------------
# SAFE EXECUTION
# -------------------------
def run_cmd(cmd):
    if not cmd:
        return

    try:
        os.system(cmd)
    except Exception as e:
        print("error:", e)


# -------------------------
# MAIN LOOP
# -------------------------
while True:
    try:
        user_input = input(prompt()).strip()

        if not user_input:
            continue

        if user_input in ["exit", "quit"]:
            break

        if user_input == "add cmd":
            add_cmd()
            continue

        if user_input == "rename":
            rename_user()
            continue

        translated = translate(user_input)
        run_cmd(translated)

    except Exception as e:
        print("shell error:", e)
