# -*- coding: utf-8 -*-
import subprocess
import time
import win32gui
import win32process
import psutil  # 仅用这个库获取PID，一行搞定

# 配置路径
SCRCPY_EXE_PATH = "scrcpy.exe"

# 静默启动scrcpy
subprocess.Popen([SCRCPY_EXE_PATH], creationflags=subprocess.CREATE_NO_WINDOW)

# -------------------------- 核心：一行获取scrcpy.exe的PID (psutil极简写法) --------------------------
def get_scrcpy_pid():
    for proc in psutil.process_iter(["pid", "name"]):
        if "scrcpy.exe" in proc.info["name"].lower():
            return proc.info["pid"]
    return None

# 通过PID获取窗口句柄
def get_hwnd_by_pid(pid):
    hwnd_target = None
    def enum_cb(hwnd, _):
        nonlocal hwnd_target
        if win32gui.IsWindowVisible(hwnd):
            _, wp = win32process.GetWindowThreadProcessId(hwnd)
            if wp == pid:
                hwnd_target = hwnd
                return False
        return True
    win32gui.EnumWindows(enum_cb, None)
    return hwnd_target

# 等待PID和句柄
scrcpy_pid = None
for _ in range(30):
    scrcpy_pid = get_scrcpy_pid()
    if scrcpy_pid: break
    time.sleep(0.5)
if not scrcpy_pid: exit("❌ 无scrcpy进程")
print(f"✅ PID = {scrcpy_pid}")

hwnd = None
for _ in range(20):
    hwnd = get_hwnd_by_pid(scrcpy_pid)
    if hwnd: break
    time.sleep(0.3)
if not hwnd: exit("❌ 无窗口")
print(f"✅ 窗口句柄 = {hwnd}")

# 监听尺寸
last_size = None
print("✅ 开始监听尺寸变化")
while win32gui.IsWindow(hwnd):
    l,t,r,b = win32gui.GetClientRect(hwnd)
    size = (r-l, b-t)
    if size != last_size:
        print(f"📱 {size[0]} × {size[1]}")
        last_size = size
    time.sleep(0.1)