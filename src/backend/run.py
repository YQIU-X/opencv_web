import subprocess
import os

root = "./src/backend/"
def run_scripts():
    point_process = subprocess.Popen(["python", os.path.join(root, "PointCallBack.py")])

    right_touch_bar_process = subprocess.Popen(["python", os.path.join(root, "RightTouchBar.py")])

    try:
        point_process.wait()
        right_touch_bar_process.wait()
    except KeyboardInterrupt:
        print("Stopping scripts...")

        point_process.terminate()
        right_touch_bar_process.terminate()

        point_process.wait()
        right_touch_bar_process.wait()

    print("Both scripts have finished.")

if __name__ == "__main__":
    run_scripts()
