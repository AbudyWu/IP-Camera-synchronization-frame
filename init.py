import os

def newname(save_dir):
    existing_files = os.listdir(save_dir)
    existing_files = [f for f in existing_files if f.endswith('.mp4')]
    if existing_files:
        existing_files.sort()
        latest_file = existing_files[-1]
        latest_number = int(latest_file.split('-')[0])
        return latest_number + 1
    else:
        return 1

def save2(save_dir):
    save_dir1 = os.path.join(save_dir, 'camera108')
    save_dir2 = os.path.join(save_dir, 'camera109')

    os.makedirs(save_dir1, exist_ok=True)
    os.makedirs(save_dir2, exist_ok=True)

    latest_number1 = newname(save_dir1)
    latest_number2 = newname(save_dir2)

    return latest_number1, latest_number2
