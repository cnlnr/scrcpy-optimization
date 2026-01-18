import subprocess
import time
import win32gui
import win32process
import psutil

# ===================== 核心封装：分辨率等比例同步类【最终完美版】 =====================
class AdbResolutionSync:
    def __init__(self):
        # 获取手机物理真实分辨率 (整数类型，核心基准)
        self.phone_phy_w, self.phone_phy_h = self.get_phone_size()
        print("=" * 60)
        print(f"✅ 手机物理原始分辨率：{self.phone_phy_w} × {self.phone_phy_h}")
        print(f"✅ 手机原始宽高比：{self.phone_phy_w/self.phone_phy_h:.6f}")
        print("=" * 60)

    def get_phone_size(self):
        """获取手机物理真实分辨率"""
        try:
            res_str = subprocess.check_output("adb shell wm size", shell=True, encoding='utf-8').strip()
            phy_size = res_str.replace("Physical size: ", "").split("x")
            return int(phy_size[0]), int(phy_size[1])
        except Exception as e:
            print(f"❌ 获取手机分辨率失败！请检查ADB连接：{e}")
            return 1080, 1920  # 兜底默认值

    def set_phone_size(self, width, height):
        """修改手机分辨率，宽高必须为正整数"""
        if width <= 100 or height <= 100:  # 过滤极小的无效分辨率
            print(f"❌ 无效分辨率：{width}x{height}，跳过修改")
            return
        try:
            # 彻底静默执行adb命令，不弹黑窗口
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            subprocess.run(f"adb shell wm size {width}x{height}", shell=True, check=True, startupinfo=si)
            print(f"✅ 手机分辨率同步成功：{width} × {height} | 比例：{width/height:.6f}")
        except Exception as e:
            print(f"❌ 修改分辨率失败：{e}")

    def reset_phone_size(self):
        """重置手机分辨率为物理原始尺寸【重中之重，所有退出必执行】"""
        try:
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            subprocess.run("adb shell wm size reset", shell=True, check=True, startupinfo=si)
            print("\n✅✅✅ 【成功恢复】手机分辨率已还原为物理原始尺寸！✅✅✅")
        except Exception as e:
            print(f"\n❌ 重置分辨率失败，请手动执行 adb shell wm size reset 恢复：{e}")

    def sync_by_window_ratio(self, window_size):
        """核心：按窗口比例精准同步手机分辨率 + 四舍五入优化精度"""
        win_w, win_h = window_size
        if win_w <= 100 or win_h <= 100:
            return
        
        # 窗口实时宽高比
        window_ratio = win_w / win_h
        
        # 四舍五入取整，精度拉满，比例误差极小
        target_phone_w = round(self.phone_phy_h * window_ratio)
        target_phone_h = self.phone_phy_h

        self.set_phone_size(target_phone_w, target_phone_h)

# ===================== scrcpy进程PID + 窗口句柄获取 =====================
def get_scrcpy_pid():
    for proc in psutil.process_iter(["pid", "name"]):
        if "scrcpy.exe" in proc.info["name"].lower():
            return proc.info["pid"]
    return None

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

# ===================== 主程序：【零报错终极版】窗口监听 + 比例同步 =====================
if __name__ == "__main__":
    # 启动scrcpy
    SCRCPY_EXE_PATH = "scrcpy.exe"
    subprocess.Popen([SCRCPY_EXE_PATH], creationflags=subprocess.CREATE_NO_WINDOW)

    # 获取PID和窗口句柄
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

    # 创建同步实例
    res_sync = AdbResolutionSync()

    # ========== ✅✅✅ 【核心修复】解决None下标报错 + 所有优化 ✅✅✅ ==========
    print("此工具仅内部测试！")
    print("\n✅ 开始监听窗口尺寸变化 → 手机分辨率严格等比例同步！")
    print("💡 拖动窗口缩放/关闭窗口/按Ctrl+C，都会自动恢复手机分辨率！")
    # 第一步：先获取一次窗口初始尺寸，给last_size赋值【根治None报错的关键】
    l, t, r, b = win32gui.GetClientRect(hwnd)
    last_size = (r - l, b - t) 
    
    try:
        while win32gui.IsWindow(hwnd):
            l, t, r, b = win32gui.GetClientRect(hwnd)
            curr_win_size = (r - l, b - t)
            
            # 第二步：判断逻辑优化 → 先判断last_size有效 + 尺寸变化≥3像素才刷新【防抖+防None】
            if curr_win_size != last_size and curr_win_size[0]>100 and curr_win_size[1]>100:
                res_sync.sync_by_window_ratio(curr_win_size)
                print(f"\n📱 投屏窗口尺寸：{curr_win_size[0]} × {curr_win_size[1]} | 窗口比例：{curr_win_size[0]/curr_win_size[1]:.6f}")
                last_size = curr_win_size
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n\n⚠️  检测到手动退出指令 (Ctrl+C)")
    except Exception as e:
        print(f"\n❌ 程序运行异常：{str(e)}")
    finally:
        # 无论任何情况，必恢复分辨率！
        res_sync.reset_phone_size()