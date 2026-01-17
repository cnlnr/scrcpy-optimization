import subprocess
import time
import psutil
import win32gui
import win32process

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
# 获取客户区尺寸
# -------------------------------
def get_client_size(hwnd):
    left, top, right, bottom = win32gui.GetClientRect(hwnd)
    width = right - left
    height = bottom - top
    return width, height

# -------------------------------
# 监听客户区大小变化
# -------------------------------
last_size = None
print("开始监听 scrcpy 窗口内部区域大小（拖动窗口试试）")
while win32gui.IsWindow(hwnd):
    size = get_client_size(hwnd)
    if size != last_size:
        print(f"客户区: {size[0]}x{size[1]} px")
        last_size = size
    time.sleep(0.1)

print("scrcpy 窗口已关闭")
