#!/usr/bin/env python3
import json
import subprocess
import re
import time
import psutil

# --- 滑鼠位置判斷邏輯 ---
def get_mouse_pos():
    try:
        pos = subprocess.run(["hyprctl", "-j", "cursorpos"], capture_output=True, text=True).stdout.strip()
        data = json.loads(pos)
        return data['x'], data['y']
    except:
        return 0, 0

# 動態島區域座標
# x1, x2 = 800, 1100
# y1, y2 = 10, 60
# last_text = ""
state = "collapsed"  # 初始狀態
hover_cooldown = 0

# --- 音量資訊函式 ---
def get_volume(text_length=10):
    try:
        output = subprocess.getoutput("pactl get-sink-volume @DEFAULT_SINK@")
        volume = int(output.split("/")[1].strip().replace("%", ""))

        mute_output = subprocess.getoutput("pactl get-sink-mute @DEFAULT_SINK@")
        is_muted = "yes" in mute_output

        if is_muted:
            icon = "🔇"
        elif volume < 30:
            icon = "🔈"
        elif volume < 70:
            icon = "🔉"
        else:
            icon = "🔊"

        # 條狀圖顯示
        bar_len = 10 if text_length <= 30 else 20
        filled = int(volume / 100 * bar_len)
        bar = "█" * filled + "░" * (bar_len - filled)
        # bar = "8" + "=" * filled + "D"

        return f"{icon} {bar} {volume}%"
    except Exception as e:
        return f"❌ {e}"

# --- 網路資訊函式 ---
def get_network():
    try:
        iface = subprocess.getoutput("ip route | grep '^default' | head -n1 | awk '{print $5}'").strip()
        ip_info = subprocess.getoutput(f"ip -4 addr show {iface}")
        match = re.search(r'inet (\d+\.\d+\.\d+\.\d+)', ip_info)
        ip = match.group(1) if match else "未取得 IP"
        return f"📶 {iface} {ip}"
    except Exception as e:
        return f"📶 無連線"
    
def get_active_window(small=False):
    try:
        running = subprocess.run(["hyprctl", "-j", "activewindow"], capture_output=True, text=True).stdout.strip()
        if small:
            return json.loads(running).get("title", "無活動視窗").split("-")[-1]
        return json.loads(running).get("title", "無活動視窗")
    except:
        return "無法取得視窗"

def get_cpu_usage():
    # 取得 CPU 百分比（整體）
    return psutil.cpu_percent(interval=0.02)

def get_ram_usage():
    mem = psutil.virtual_memory()
    # 取得 RAM 使用率百分比
    return mem.percent

# 這是計算網路速度的函式，需記錄前一次的數值做差分
net_io_prev = psutil.net_io_counters()

def get_network_speed():
    global net_io_prev
    net_io_current = psutil.net_io_counters()
    # bytes per second
    upload_speed = (net_io_current.bytes_sent - net_io_prev.bytes_sent) / 1
    download_speed = (net_io_current.bytes_recv - net_io_prev.bytes_recv) / 1
    net_io_prev = net_io_current

    # 換算成 KB/s，取整數
    upload_kb = int(upload_speed / 1024)
    download_kb = int(download_speed / 1024)
    return upload_kb, download_kb

while True:
    # 決定這一輪要顯示的文字
    if state == "expanded":
        text = f"{get_active_window()} \n{get_volume(len(get_active_window()))} \n{get_network()} ⬆️: {get_network_speed()[0]} KB/s ⬇️: {get_network_speed()[1]} KB/s\n {get_cpu_usage()}% CPU {get_ram_usage()}% RAM"
        klass = "expanded"
    else:
        text = get_active_window()
        klass = "collapsed"

    # 用文字內容決定 hover 區域
    if "\n" in text:
        display_line = sorted(text.split("\n"), key=len, reverse=True)[0]
    else:
        display_line = text

    x1 = 960 - (len(display_line) * 8 / 2) - 18
    x2 = 960 + (len(display_line) * 8 / 2) + 18
    y1 = 10
    y2 = 10 + len(text.split("\n")) * 30 + 10

    x, y = get_mouse_pos()
    inside = x1 <= x <= x2 and y1 <= y <= y2

    if inside:
        state = "expanded"
        hover_cooldown = 1
    else:
        if hover_cooldown > 0:
            hover_cooldown -= 1
        else:
            state = "collapsed"

    print(json.dumps({"text": text.strip(), "class": klass}), flush=True)