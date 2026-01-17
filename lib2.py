import subprocess
import time
import psutil
import win32gui
import win32process
import ctypes

SCRCPY_VBS = "scrcpy-noconsole.vbs"
SCRCPY_PROCESS_KEYWORD = "scrcpy"

ctypes.windll.shcore.SetProcessDpiAwareness(2)

# ----------------------------
# 1. 启动 scrcpy
# ----------------------------
def start_scrcpy_vbs():
    """
    通过 VBS 启动 scrcpy，无控制台
    """
    subprocess.Popen(
        SCRCPY_VBS,
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


# ----------------------------
# 2. 查找 scrcpy.exe PID
# ----------------------------
def find_scrcpy_pid(timeout=5):
    start = time.time()
    while time.time() - start < timeout:
        for p in psutil.process_iter(["pid", "name"]):
            name = p.info["name"]
            if name and SCRCPY_PROCESS_KEYWORD in name.lower():
                return p.info["pid"]
        time.sleep(0.1)
    return None


# ----------------------------
# 3. 按 PID 查找顶层窗口
# ----------------------------
def find_window_by_pid(pid):
    hwnds = []

    def enum_handler(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd):
            return
        _, win_pid = win32process.GetWindowThreadProcessId(hwnd)
        if win_pid == pid:
            hwnds.append(hwnd)

    win32gui.EnumWindows(enum_handler, None)
    return hwnds


# ----------------------------
# 4. 确定渲染窗口
# ----------------------------
def find_render_window(hwnd):
    """
    尝试找渲染子窗口，如果没有子窗口，返回顶层窗口
    """
    children = []

    def enum_child(child, _):
        if not win32gui.IsWindowVisible(child):
            return
        left, top, right, bottom = win32gui.GetClientRect(child)
        w = right - left
        h = bottom - top
        if w > 0 and h > 0:
            children.append((w * h, child))

    win32gui.EnumChildWindows(hwnd, enum_child, None)

    if children:
        children.sort(reverse=True)
        return children[0][1]

    return hwnd  # 没有子窗口，顶层窗口即渲染窗口


# ----------------------------
# 5. 获取窗口尺寸
# ----------------------------
def get_sizes(hwnd):
    """
    获取窗口多种尺寸信息
    - 客户区大小（内容区）
    - 窗口外框大小（含边框和标题栏）
    - 物理像素大小（考虑 DPI 缩放）
    """
    # 客户区大小
    left, top, right, bottom = win32gui.GetClientRect(hwnd)
    client_width = right - left
    client_height = bottom - top

    # 窗口外框大小（含边框、标题栏）
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    window_width = right - left
    window_height = bottom - top

    # 获取窗口 DPI（Windows 10+）
    try:
        dpi = ctypes.windll.shcore.GetDpiForWindow(hwnd)
    except Exception:
        dpi = 96  # 默认标准 DPI

    physical_width = int(window_width * dpi / 96)
    physical_height = int(window_height * dpi / 96)

    return (client_width, client_height), (window_width, window_height), (physical_width, physical_height)


# ----------------------------
# 6. 监听窗口大小变化
# ----------------------------
def monitor_size(hwnd):
    last_sizes = None
    print("开始监听 scrcpy 窗口大小（拖动窗口试试）")

    while win32gui.IsWindow(hwnd):
        client_size, window_size, physical_size = get_sizes(hwnd)

        if (client_size, window_size, physical_size) != last_sizes:
            print(f"客户区大小: {client_size[0]} x {client_size[1]} px | "
                  f"窗口外框大小: {window_size[0]} x {window_size[1]} px | "
                  f"物理像素: {physical_size[0]} x {physical_size[1]} px")
            last_sizes = (client_size, window_size, physical_size)

        time.sleep(0.05)

    print("scrcpy 已关闭")


# ----------------------------
# 主流程
# ----------------------------
def main():
    print("启动 scrcpy-noconsole.vbs …")
    start_scrcpy_vbs()

    print("等待 scrcpy.exe 进程 …")
    pid = find_scrcpy_pid()
    if not pid:
        print("❌ 未找到 scrcpy.exe 进程")
        return

    print(f"✅ 找到 scrcpy.exe PID = {pid}")

    print("查找 scrcpy 顶层窗口 …")
    hwnd = None
    for _ in range(50):
        hwnds = find_window_by_pid(pid)
        if hwnds:
            hwnd = hwnds[0]
            break
        time.sleep(0.1)

    if not hwnd:
        print("❌ 未找到 scrcpy 顶层窗口")
        return

    print("锁定 scrcpy 渲染窗口 …")
    render_hwnd = find_render_window(hwnd)

    print("✅ 已锁定渲染窗口，开始监听")
    monitor_size(render_hwnd)


if __name__ == "__main__":
    main()
