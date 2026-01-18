import subprocess
import time
import win32gui

SCRCPY_EXE_PATH = "scrcpy.exe"
subprocess.Popen([SCRCPY_EXE_PATH], creationflags=subprocess.CREATE_NO_WINDOW)

# 微软官方标准写法：枚举+筛选
def get_scrcpy_hwnd():
    target = None
    def enum_cb(hwnd, _):
        nonlocal target
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetClassName(hwnd) == "SDL_app":
            target = hwnd
            return False
        return True
    win32gui.EnumWindows(enum_cb, None)
    return target

hwnd = None
for _ in range(50):
    hwnd = get_scrcpy_hwnd()
    if hwnd: break
    time.sleep(0.3)

if not hwnd: exit("❌ 未找到窗口")
print(f"✅ 句柄: {hwnd}")

last_size = None
while win32gui.IsWindow(hwnd):
    l,t,r,b = win32gui.GetClientRect(hwnd)
    size = (r-l, b-t)
    if size != last_size:
        print(f"📱 {size[0]} × {size[1]}")
        last_size = size
    time.sleep(0.1)