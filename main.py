import subprocess
import time
import psutil
import win32gui
import win32process
import ctypes

# -------------------------------
# 启动 scrcpy
# -------------------------------
subprocess.Popen(["scrcpy-noconsole.vbs"], shell=True)

# -------------------------------
# 等待 scrcpy.exe 出现
# -------------------------------
pid = None
for _ in range(50):
    for p in psutil.process_iter(["pid", "name"]):
        if "scrcpy" in (p.info["name"] or "").lower():
            pid = p.info["pid"]
            break
    if pid:
        break
    time.sleep(3)

if not pid:
    print("未找到 scrcpy.exe")
    exit()

# -------------------------------
# 枚举顶层窗口按 PID
# -------------------------------
def find_hwnd_by_pid(pid):
    hwnds = []
    def enum_handler(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            _, win_pid = win32process.GetWindowThreadProcessId(hwnd)
            if win_pid == pid:
                hwnds.append(hwnd)
    win32gui.EnumWindows(enum_handler, None)
    return hwnds

hwnds = find_hwnd_by_pid(pid)
print("找到的窗口句柄:", hwnds)

if not hwnds:
    exit()

hwnd = hwnds[0]  # 取第一个窗口句柄

# -------------------------------
# 设置 DPI 感知（确保物理像素正确）
# -------------------------------
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)  # Per-monitor DPI aware
except Exception:
    pass

# -------------------------------
# 获取窗口多种尺寸
# -------------------------------
def get_window_sizes(hwnd):
    # 客户区大小
    left, top, right, bottom = win32gui.GetClientRect(hwnd)
    client_width = right - left
    client_height = bottom - top

    # 窗口外框大小（含边框、标题栏）
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    window_width = right - left
    window_height = bottom - top

    # 物理像素
    try:
        dpi = ctypes.windll.shcore.GetDpiForWindow(hwnd)
    except Exception:
        dpi = 96
    physical_width = int(window_width * dpi / 96)
    physical_height = int(window_height * dpi / 96)

    return (client_width, client_height), (window_width, window_height), (physical_width, physical_height)

# -------------------------------
# 监听窗口大小变化
# -------------------------------
last_sizes = None
print("开始监听 scrcpy 窗口大小（拖动窗口试试）")
while win32gui.IsWindow(hwnd):
    client_size, window_size, physical_size = get_window_sizes(hwnd)
    if (client_size, window_size, physical_size) != last_sizes:
        print(f"客户区: {client_size[0]}x{client_size[1]} px | "
              f"窗口外框: {window_size[0]}x{window_size[1]} px | "
              f"物理像素: {physical_size[0]}x{physical_size[1]} px")
        last_sizes = (client_size, window_size, physical_size)
    time.sleep(0.1)

print("scrcpy 窗口已关闭")
