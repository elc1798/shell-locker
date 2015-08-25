#!/usr/local/bin/python3

'''
This is a verification mechanism for logging on to my zShell
'''

import os, sys, subprocess
import time
import getpass, hashlib, binascii
import atexit
import argparse

# Check for Python3

if sys.version_info[0] < 3:
    print("ShellLocker requires Python 3 or higher.")
    exit()

# Silence Python internal error messages

class DevNull:
    def write(self, msg):
        pass

sys.stderr = DevNull()

# Declare Terminal ANSI colors

class ansi_colors:
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    RESET = "\033[0m"

# Set variable for current location of script

SCRIPT_PATH = os.path.realpath(__file__)

def invalidate():
    print("")
    if os.access(SCRIPT_PATH, os.X_OK):
        os.system(SCRIPT_PATH)
    else:
        os.system("python3 " + SCRIPT_PATH)

def verify():
    f = open(os.path.dirname(SCRIPT_PATH) + "/shelllocker.conf" , 'r')
    DATA = f.read().replace(" " , "")
    f.close()
    # Check header:
    if DATA[0:34] != "7368656c6c6c6f636b6572686561646572":
        print(ansi_colors.RED + "Invalid configuration file!" + ansi_colors.RESET)
        print(ansi_colors.RED + "Fatal internal error occured" + ansi_colors.RESET)
        exit()
    DATA = DATA[34:]
    # First byte = length of username
    USER_LEN = int(DATA[0:2])
    DATA = DATA[2:]
    USERNAME = "".join(DATA[i:i+1] for i in range(0, USER_LEN * 2))
    PASSWORD = DATA[USER_LEN * 2:]

    user = binascii.hexlify(getpass.getuser().encode('utf-8')).decode()
    if user != USERNAME:
        print(ansi_colors.RED + "User not recognized!" + ansi_colors.RESET)
        invalidate()
    response = str(getpass.getpass("shell_auth: "))
    m = hashlib.md5()
    m.update(response.encode('utf-8'))
    if m.hexdigest() == PASSWORD:
        atexit.unregister(invalidate)
        exit()
    else:
        print("Incorrect.")
        blankshell()

def blankshell():
    print("Use the command <help> to list all the commands.")
    while True:
        user_query = input(ansi_colors.GREEN + "[limbo_shell]" + ansi_colors.RESET + "$ ")
        if user_query == 'start_t':
            verify()
        elif user_query == 'clear':
            print("\033\143", end="", flush=True)
        elif user_query == 'help':
            print("start_t | Starts the auth engine for terminal session")
            print("clear   | Clears the screen")
            print("help    | Displays this message")

def setup():
    configured = 'shelllocker.conf' in [f for f in os.listdir('.') if os.path.isfile(f)]
    if configured:
        print(ansi_colors.YELLOW + "ShellLocker is already configured." + ansi_colors.RESET)
        print(ansi_colors.YELLOW + "Use the '--reset' flag to remove configurations" + ansi_colors.RESET)
        exit()
    else:
        new_pass = str(getpass.getpass("Set your shell password: ")).encode('utf-8')
        new_pass_confirm = str(getpass.getpass("Confirm your password: ")).encode('utf-8')
        if new_pass != new_pass_confirm:
            print("Passwords did not match.")
            exit()
        else:
            m = hashlib.md5()
            m.update(new_pass)
            HASHED_PASS = m.hexdigest()
            USER = binascii.hexlify(getpass.getuser().encode('utf-8')).decode()
            DATA = "73 68 65 6c 6c 6c 6f 63 6b 65 72 68 65 61 64 65 72 "
            if len(USER) % 2 == 1:
                USER = "0" + USER
            USER_LEN = str(int(len(USER) / 2))
            if int(USER_LEN) >= 100:
                print(ansi_colors.RED + "Fatal internal error occured" + ansi_colors.RESET)
                exit()
            if len(USER_LEN) % 2 == 1:
                USER_LEN = "0" + USER_LEN
            if len(HASHED_PASS) % 2 == 1:
                HASHED_PASS = "0" + HASHED_PASS
            DATA += ' '.join(USER_LEN[i:i+2] for i in range(0,len(USER_LEN),2)) + " "
            DATA += ' '.join(USER[i:i+2] for i in range(0,len(USER),2)) + " "
            DATA += ' '.join(HASHED_PASS[i:i+2] for i in range(0,len(HASHED_PASS),2)) + " "
            f = open(os.path.dirname(SCRIPT_PATH) + "/shelllocker.conf" , 'w')
            f.write(DATA)
            f.close()

def reset():
    if subprocess.call(["sudo" , "-k" , "-v" , "-p" , "[Verify] Root password: "]) != 0:
        print(ansi_colors.RED + "Fatal internal error occured" + ansi_colors.RESET)
        print(ansi_colors.RED + "Incorrect root password!" + ansi_colors.RESET)
        exit()
    else:
        os.remove(os.path.dirname(SCRIPT_PATH) + "/shelllocker.conf")
        setup()

def diagnose():
    if SCRIPT_PATH != os.path.expanduser("~") + "/.shelllocker/main.py":
        print(ansi_colors.YELLOW + "ShellLocker program files are in " + SCRIPT_PATH + ansi_colors.RESET)
        print(ansi_colors.YELLOW + "ShellLocker program files should be in ~/.shelllocker" + ansi_colors.RESET)
        responded = False
        while not responded:
            conf = str(input("Fix? (Y/N): "))
            if conf in ['N' , 'n']:
                responded = True
            elif conf in ['Y' , 'y']:
                responded = True
                # Fix the issue here
    if not os.access(SCRIPT_PATH, os.X_OK):
        print(ansi_colors.RED + "Script is not an executable!" + ansi_colors.RESET)
        esponded = False
        while not responded:
            conf = str(input("Fix? (Y/N): "))
            if conf in ['N' , 'n']:
                responded = True
            elif conf in ['Y' , 'y']:
                responded = True
                os.system("chmod +x " + SCRIPT_PATH)
    if 'shelllocker.conf' not in [f for f in os.listdir('.') if os.path.isfile(f)]:
        print(ansi_colors.YELLOW + "shelllocker.conf not found" + ansi_colors.RESET)
        print(ansi_colors.YELLOW + "Run with '-s' flag to generate the file" + ansi_colors.RESET)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s",
        "--setup",
        help="Run the setup script",
        action="store_true"
    )
    parser.add_argument(
        "-d",
        "--diagnose",
        help="Check to see if dependencies for this program are met",
        action="store_true"
    )
    parser.add_argument(
        "--reset",
        help="Resets ShellLocker configurations",
        action="store_true"
    )
    args = parser.parse_args()
    if args.setup:
        setup()
    elif args.diagnose:
        diagnose()
    elif args.reset:
        reset()
    else:
        atexit.register(invalidate)
        blankshell()

if __name__ == "__main__":
    main()
