class AutoResolution:
    def __init__(self):
        self.phone_width, self.phone_height = self.get_phone_resolution()
        self.original_resolution = (self.phone_width, self.phone_height)

    @staticmethod
    def wm_size(width, height):
        subprocess.run(f"adb shell wm size {width}x{height}", shell=True)

    @staticmethod
    def reset():
        subprocess.run("adb shell wm size reset", shell=True)

    @staticmethod
    def get_phone_resolution():
        resolution = subprocess.check_output("adb shell wm size", shell=True, encoding='utf-8') \
                               .splitlines()[0].removeprefix("Physical size: ").split("x")
        w, h = map(int, resolution)
        return w, h

    def get_scaled_resolution(self, win_width, win_height):
        """根据窗口尺寸计算新的手机分辨率（保持等比例）"""
        scale = min(win_width / self.phone_width, win_height / self.phone_height)
        new_width = int(self.phone_width * scale)
        new_height = int(self.phone_height * scale)
        return new_width, new_height

    def apply_scaled_resolution(self, win_width, win_height):
        """窗口尺寸已知时修改手机分辨率"""
        new_w, new_h = self.get_scaled_resolution(win_width, win_height)
        print(f"修改分辨率为: {new_w}x{new_h}")
        self.wm_size(new_w, new_h)

    def restore_original(self):
        print(f"恢复分辨率为: {self.original_resolution[0]}x{self.original_resolution[1]}")
        self.reset()



import time

# 假设上面已经定义了 AutoResolution 类
# from your_module import AutoResolution

if __name__ == "__main__":
    # 初始化
    auto_res = AutoResolution()
    print("设备原始分辨率:", auto_res.original_resolution)

    # -----------------------------
    # 模拟窗口变化
    # -----------------------------
    # 假设 scrcpy 窗口被拖动到 720x1280
    win_w, win_h = 720, 1280
    print(f"窗口大小变化: {win_w}x{win_h}")

    # 自动按窗口大小修改手机分辨率
    auto_res.apply_scaled_resolution(win_w, win_h)

    # 再模拟窗口变大到 1080x1920
    time.sleep(2)
    win_w, win_h = 1080, 1920
    print(f"窗口大小变化: {win_w}x{win_h}")
    auto_res.apply_scaled_resolution(win_w, win_h)

    # -----------------------------
    # 恢复原始分辨率
    # -----------------------------
    print("等待 3 秒后恢复原分辨率")
    time.sleep(3)
    auto_res.restore_original()
