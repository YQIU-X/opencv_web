import subprocess
import os

root = "./src/backend/"
def run_scripts():
    process = []
    load_images_process = subprocess.Popen(["python", os.path.join(root,"basic/Load_Images.py")])
    upload_images_process = subprocess.Popen(["python", os.path.join(root,"basic/Upload_Images.py")])
    adjust_img_process = subprocess.Popen(["python", os.path.join(root, "basic/Adjust_Img.py")])
    draw_hist_process = subprocess.Popen(["python", os.path.join(root,"basic/Draw_Hist.py")])
    remove_img_process = subprocess.Popen(["python", os.path.join(root, "basic/Remove_Image.py")])
    next_img_process = subprocess.Popen(["python", os.path.join(root,"basic/Next_Image.py")])
    undo_action_process = subprocess.Popen(["python", os.path.join(root, "basic/Undo_Action.py")])
    point_callback_process = subprocess.Popen(["python", os.path.join(root, "basic/Point_Callback.py")])

    style_migration_process = subprocess.Popen(["python", os.path.join(root, "NN/Style_Migration.py")])
    seg_human_process = subprocess.Popen(["python", os.path.join(root, "PP_HumanSeg/Seg_Human.py")])

    process.append(load_images_process)
    process.append(upload_images_process)
    process.append(adjust_img_process)
    process.append(draw_hist_process)
    process.append(remove_img_process)
    process.append(next_img_process)
    process.append(undo_action_process)
    process.append(style_migration_process)
    process.append(seg_human_process)
    # process.append(point_callback_process)

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
