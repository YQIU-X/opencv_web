import subprocess
import os

root = "./src/backend/"
def run_scripts():
    process = []
    # point_process = subprocess.Popen(["python", os.path.join(root, "/basic/PointCallBack.py")])
    # draw_hist = subprocess.Popen(["python", os.path.join(root,"/basic/DrawHist.py")])
    load_images_process = subprocess.Popen(["python", os.path.join(root,"basic/Load_Images.py")])
    upload_images_process = subprocess.Popen(["python", os.path.join(root,"basic/Upload_Images.py")])
    adjust_img_process = subprocess.Popen(["python", os.path.join(root, "basic/Adjust_Img.py")])
    draw_hist_process = subprocess.Popen(["python", os.path.join(root,"basic/Draw_Hist.py")])
    process.append(load_images_process)
    process.append(upload_images_process)
    process.append(adjust_img_process)
    process.append(draw_hist_process)


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
