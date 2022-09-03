import os
from typing import Tuple

from PIL import Image

# ## CONFIG ##
searching_dir = ["./gtFine/", "./leftImg8bit"]
file_list = []


def access_dir(path):
    dir_list = os.listdir(path)
    for obj in dir_list:
        full_path = os.path.join(path, obj)

        if os.path.isdir(full_path):
            print("detected folder: " + obj)
            access_dir(full_path)
        else:
            # print('found file: ' + full_path)
            file_list.append(full_path)


def resizeImg(img_path):
    print("processing : " + img_path)
    img = Image.open(img_path)
    width, height = img.size
    ratio = width / height

    if width > 1920 and height > 1200:
        print('sizes ok')  # 7680 * 4320
    else:
        print('size smaller')

    min_width = int(ratio * 1200)
    horizontal_margin = (min_width - 1920) / 2

    img = img.resize((min_width, 1200), Image.LANCZOS)
    crop_box: tuple[float, int, float, int] = (horizontal_margin, 0, min_width - horizontal_margin, 1200)
    img = img.crop(crop_box)
    img.save(img_path)
    # print(img.size)


for path in searching_dir:
    access_dir(path)
    # print(file_list)
    for file in file_list:
        name = str(file)
        if name.endswith("leftImg8bit.png"):
            # lI8b
            resizeImg(file)
        elif name.endswith("labelTrainIds.png"):
            resizeImg(file)
        elif name.endswith("instanceIds.png"):
            resizeImg(file)
        else:
            print("not target, skipping...")

    print("done!")
