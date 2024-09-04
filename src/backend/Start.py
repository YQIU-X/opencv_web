import subprocess
import os

root = "./src/backend/"
def run_scripts():
    process = []
    load_images_process = subprocess.Popen(["python", os.path.join(root,"left_side/Load_Images.py")])
    upload_images_process = subprocess.Popen(["python", os.path.join(root,"left_side/Upload_Images.py")])

    adjust_img_process = subprocess.Popen(["python", os.path.join(root, "right_side/S1/Adjust_Img.py")])
    draw_hist_process = subprocess.Popen(["python", os.path.join(root,"right_side/S1/Draw_Hist.py")])

    free_crop_process = subprocess.Popen(["python", os.path.join(root, "right_side/S2/Crop.py")])
    cancel_crop_process = subprocess.Popen(["python", os.path.join(root,"right_side/S2/Cancel_Crop.py")])
    apply_crop_process = subprocess.Popen(["python", os.path.join(root, "right_side/S2/Apply_Crop.py")])
    update_rotation_process = subprocess.Popen(["python", os.path.join(root, "right_side/S2/Update_Rotation.py")])

    style_migration_process = subprocess.Popen(["python", os.path.join(root, "right_side/S4/Style_Migration.py")])
    seg_human_process = subprocess.Popen(["python", os.path.join(root, "right_side/S4/Seg_Human.py")])

    next_img_process = subprocess.Popen(["python", os.path.join(root,"right_side/Next_Image.py")])
    undo_action_process = subprocess.Popen(["python", os.path.join(root, "right_side/Undo_Action.py")])

    remove_img_process = subprocess.Popen(["python", os.path.join(root, "bottom_gallery/Remove_Image.py")])


    process.append(load_images_process)
    process.append(upload_images_process)
    process.append(adjust_img_process)
    process.append(draw_hist_process)
    process.append(remove_img_process)
    process.append(next_img_process)
    process.append(undo_action_process)
    process.append(style_migration_process)
    process.append(seg_human_process)
    process.append(free_crop_process)
    process.append(cancel_crop_process)
    process.append(apply_crop_process)
    process.append(update_rotation_process)

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
