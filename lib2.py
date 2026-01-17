import subprocess
import time
import sys
import pygetwindow as gw

class ScrcpyWindowManager:
    """scrcpy启动+窗口尺寸实时监控类"""
    def __init__(self, scrcpy_path="scrcpy", interval=0.2):
        """
        初始化配置
        :param scrcpy_path: scrcpy可执行文件路径，已配置环境变量则填"scrcpy"即可
        :param interval: 窗口尺寸查询间隔(秒)，默认0.2秒，值越小刷新越快
        """
        self.scrcpy_path = scrcpy_path
        self.interval = interval
        self.scrcpy_process = None  # scrcpy进程句柄
        self.scrcpy_window = None   # scrcpy窗口句柄

    def start_scrcpy(self, scrcpy_args: list = None):
        """
        启动scrcpy进程，支持传入自定义scrcpy参数
        :param scrcpy_args: scrcpy启动参数列表，例如：["--window-width", "720", "--no-audio"]
        """
        cmd = [self.scrcpy_path]
        if scrcpy_args and isinstance(scrcpy_args, list):
            cmd.extend(scrcpy_args)
        
        # 后台启动scrcpy，不阻塞主线程，屏蔽scrcpy的控制台输出
        self.scrcpy_process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=True if sys.platform == "win32" else False
        )
        print(f"✅ scrcpy启动成功，进程PID: {self.scrcpy_process.pid}")
        time.sleep(1)  # 预留1秒窗口加载时间，避免立即查询窗口失败

    def get_scrcpy_window(self):
        """获取scrcpy的窗口句柄，匹配标题包含scrcpy的窗口"""
        try:
            # 遍历所有窗口，筛选scrcpy窗口（兼容中英文标题）
            self.scrcpy_window = gw.getWindowsWithTitle("scrcpy")[0]
            return self.scrcpy_window
        except IndexError:
            return None

    def monitor_window_size(self):
        """核心方法：循环监控并打印窗口尺寸，带\r单行刷新"""
        if not self.scrcpy_process or self.scrcpy_process.poll() is not None:
            print("❌ 请先启动scrcpy进程！", flush=True)
            return

        print("\n📌 开始监控窗口尺寸，按【Ctrl+C】退出监控\n", flush=True)
        while True:
            # 循环判断：scrcpy进程是否存活 + 是否能获取窗口
            if self.scrcpy_process.poll() is not None:
                print("\n❌ scrcpy进程已退出，监控结束！", flush=True)
                break
            
            self.scrcpy_window = self.get_scrcpy_window()
            if self.scrcpy_window:
                # 获取窗口实时宽高
                win_width = self.scrcpy_window.width
                win_height = self.scrcpy_window.height
                # 核心：使用\r实现光标回到行首，单行覆盖打印，end=''取消默认换行
                print(f"🔍 窗口尺寸 -> 宽: {win_width} px | 高: {win_height} px", end="\r", flush=True)
            else:
                print("🔍 暂未检测到scrcpy窗口，重试中...", end="\r", flush=True)

            # 退出判断：scrcpy进程关闭/窗口关闭
            if not self.scrcpy_window or self.scrcpy_window.closed:
                break
            time.sleep(self.interval)

    def stop_all(self):
        """优雅退出：关闭scrcpy进程+释放资源"""
        if self.scrcpy_process and self.scrcpy_process.poll() is None:
            self.scrcpy_process.terminate()
            self.scrcpy_process.wait()
            print("\n✅ scrcpy进程已正常关闭", flush=True)
        sys.exit(0)

# 测试主程序（直接运行该文件即可生效）
if __name__ == "__main__":
    # 初始化管理器
    manager = ScrcpyWindowManager(interval=0.1)
    try:
        # 启动scrcpy，可自定义参数：比如指定窗口宽度720、关闭音频、无边框
        scrcpy_custom_args = ["--window-width", "720", "--no-audio", "--window-borderless"]
        manager.start_scrcpy(scrcpy_custom_args)
        # 开始循环监控窗口尺寸
        manager.monitor_window_size()
    except KeyboardInterrupt:
        # 捕获Ctrl+C，优雅退出
        print("\n\n⚠️  接收到退出信号，正在清理...", flush=True)
        manager.stop_all()
    except Exception as e:
        print(f"\n❌ 程序异常：{str(e)}", flush=True)
        manager.stop_all()