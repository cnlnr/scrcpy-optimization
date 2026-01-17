import subprocess

# 修改屏幕分辨率
def wm_size(width,height):
    # 使用 adb 修改屏幕分辨率
    subprocess.run(f"adb shell wm size {width}x{height}", shell=True)


def reset():
    # 使用 adb 重置屏幕分辨率
    subprocess.run("adb shell wm size reset", shell=True)


if __name__ == "__main__":
    w,h = 1080,1920
    print(f"更改为 {w}x{h}")
    wm_size(w,h)

    import time
    print("等待 5 秒后恢复")
    time.sleep(5)
    reset()