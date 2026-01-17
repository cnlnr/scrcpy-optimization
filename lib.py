import subprocess

# 修改屏幕分辨率
def wm_size(width,height):
    # 使用 adb 修改屏幕分辨率
    subprocess.run(f"adb shell wm size {width}x{height}", shell=True)





