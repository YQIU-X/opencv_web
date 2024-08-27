import subprocess
import os

root = "./src/backend/"
def run_scripts():
    process = []
    point_process = subprocess.Popen(["python", os.path.join(root, "PointCallBack.py")])

    right_touch_bar_process = subprocess.Popen(["python", os.path.join(root, "RightTouchBar.py")])

    file_floder_process = subprocess.Popen(["python", os.path.join(root, "OpenFloder.py")])

    process.append(point_process)
    process.append(right_touch_bar_process)
    process.append(file_floder_process)

    print("Starting scripts...")
    try:
        for p in process:
            p.wait()
    except KeyboardInterrupt:
        print("Stopping scripts...")
        for p in process:
            p.terminate()

        for p in process:
            p.wait()

    print("Both scripts have finished.")

if __name__ == "__main__":
    run_scripts()
