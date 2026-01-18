# -*- coding: utf-8 -*-
import subprocess
import time
import win32gui

# -------------------------- 核心配置（按需修改这1行即可） --------------------------
SCRCPY_EXE_PATH = "scrcpy.exe"  # scrcpy.exe路径，不是当前目录就写绝对路径，例："D:/scrcpy/scrcpy.exe"

# ------------------------------- 1. 静默启动 scrcpy.exe 无黑窗口 ✔️ -------------------------------
subprocess.Popen(
    [SCRCPY_EXE_PATH],
    creationflags=subprocess.CREATE_NO_WINDOW  # 无黑窗启动，替代vbs脚本
)

# ------------------------------- 2. 精准查找scrcpy窗口句柄（无标题依赖、无PID、无进程） ✔️ -------------------------------
def find_scrcpy_hwnd():
    hwnd_target = None
    def callback(hwnd, _):
        nonlocal hwnd_target
        # 核心匹配：scrcpy窗口固定类名 SDL_app + 窗口可见
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetClassName(hwnd) == "SDL_app":
            hwnd_target = hwnd
            return False  # 找到后立即终止遍历，提速
        return True
    win32gui.EnumWindows(callback, None)
    return hwnd_target

# ------------------------------- 3. 等待scrcpy窗口加载完成 -------------------------------
hwnd = None
print("正在等待scrcpy投屏窗口加载...")
for _ in range(50):
    hwnd = find_scrcpy_hwnd()
    if hwnd:
        break
    time.sleep(0.3)

if not hwnd:
    print("❌ 错误：未检测到scrcpy投屏窗口，请检查是否正常启动scrcpy")
    exit()
print(f"✅ 成功找到scrcpy窗口，窗口句柄: {hwnd}")

# ------------------------------- 4. 获取窗口【客户区】尺寸（投屏画面真实尺寸，无标题栏/边框） ✔️ -------------------------------
def get_client_size(hwnd):
    left, top, right, bottom = win32gui.GetClientRect(hwnd)
    return right - left, bottom - top

# ------------------------------- 5. 实时监听窗口尺寸变化（核心逻辑，无任何报错） ✔️ -------------------------------
last_size = None
print("✅ 开始监听投屏窗口画面尺寸变化（拖动窗口缩放即可触发）")
try:
    while win32gui.IsWindow(hwnd):  # 窗口存在就一直监听
        current_size = get_client_size(hwnd)
        if current_size != last_size:
            print(f"📱 投屏画面尺寸更新: {current_size[0]} × {current_size[1]} 像素")
            last_size = current_size
        time.sleep(0.1)  # 兼顾实时性和CPU占用
except KeyboardInterrupt:
    print("\nℹ️ 用户手动终止监听")
except Exception as e:
    print(f"\n❌ 程序异常: {str(e)}")
finally:
    print("ℹ️ scrcpy窗口已关闭，监听结束")