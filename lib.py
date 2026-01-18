import re
import subprocess

# 修改屏幕分辨率
def wm_size(width,height):
    # 使用 adb 修改屏幕分辨率
    subprocess.run(f"adb shell wm size {width}x{height}", shell=True)

# 使用 adb 重置屏幕分辨率
def reset():
    subprocess.run("adb shell wm size reset", shell=True)

# 查询设备分辨率
def size():
    resolution = subprocess.check_output("adb shell wm size", shell=True, encoding='utf-8').splitlines()[0].removeprefix("Physical size: ").split("x")
    return resolution



if __name__ == "__main__":
    w,h = 1080,1920

    print("设备分辨率：",size())
    print(f"更改为 {w}x{h}")
    wm_size(w,h)

    import time
    print("等待 3 秒后恢复")
    time.sleep(3)
    reset()