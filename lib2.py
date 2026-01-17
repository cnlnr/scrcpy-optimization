import subprocess
import time
import psutil
import win32gui
import win32process


SCRCPY_VBS = "scrcpy-noconsole.vbs"
SCRCPY_PROCESS_KEYWORD = "scrcpy"


def start_scrcpy_vbs():
    subprocess.Popen(
        SCRCPY_VBS,
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def find_scrcpy_pid(timeout=5):
    start = time.time()
    while time.time() - start < timeout:
        for p in psutil.process_iter(["pid", "name"]):
            name = p.info["name"]
            if name and SCRCPY_PROCESS_KEYWORD in name.lower():
                return p.info["pid"]
        time.sleep(0.1)
    return None


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


def find_render_window(hwnd):
    """
    尝试找渲染子窗口；
    如果没有子窗口，直接返回顶层窗口
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

    # ⭐ 关键修正点：没有子窗口 → 顶层窗口本身就是渲染窗口
    return hwnd


def get_client_size(hwnd):
    left, top, right, bottom = win32gui.GetClientRect(hwnd)
    return right - left, bottom - top


def monitor_size(hwnd):
    last = None
    print("开始监听 scrcpy 窗口大小（拖动窗口试试）")

    while win32gui.IsWindow(hwnd):
        size = get_client_size(hwnd)
        if size != last:
            print(f"scrcpy 渲染区大小变化: {size[0]} x {size[1]}")
            last = size
        time.sleep(0.05)

    print("scrcpy 已关闭")


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
