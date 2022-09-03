import json
import os
import shutil
import threading
from PIL import Image
from cityscapesscripts.preparation.json2instanceImg import json2instanceImg
from cityscapesscripts.preparation.json2labelImg import json2labelImg
from loguru import logger
from rich.progress import Progress

# ================ CONFIG ================ #

structure_folders: list[str] = []
source_folder_names = ['raw/json', 'raw/img']
city_names = ['fsacI', 'fsacII']
output_img_options = ["trainIds", "ids"]
train_file_num = -1
val_file_num = -1
# 'r' stands for relative.

# ================ CONFIG ================ #

check = 0
TOTAL = train_file_num + val_file_num


# class PercentageThread(threading.Thread):
#
#     def __init__(self):
#         threading.Thread.__init__(self)
#         self.id_list = []
#         self.id = None
#         self.progress = Progress()
#
#     def add(self, msg):
#         id = self.progress.add_task(msg)
#         self.id_list.append(id)
#         return id
#
#     def update(self, id, advance=1):
#         self.progress.update(id, advance=advance)


class CvtImgThread(threading.Thread):
    def __init__(self, ID):
        threading.Thread.__init__(self)
        self.ID = ID

    def run(self):  # Not Tested
        print('asd')
        for i in range(0, 19):
            path = "./raw/img" + str(self.ID * 20 + i)
            if os.path.exists(path + '.jpg'):
                logger.info("Converting image: " + path + '.jpg')
                img = Image.open(path + '.jpg')
                img.save(path + '.png')

                os.remove(path + '.jpg')
            else:
                logger.info("(Interrupted by file non-exist) | Image Converting Completed")
                break


class GenImgThread(threading.Thread):
    def __init__(self, ID, start_pos, counts, sf_pos, oio_pos):
        threading.Thread.__init__(self)
        self.ID = ID
        self.start_pos = start_pos
        self.counts = counts
        self.sf_pos: int = sf_pos
        self.oio_pos: int = oio_pos

    def run(self):
        for i in range(self.start_pos, self.counts):
            seq_num = str(i).rjust(6, '0')
            output_type = output_img_options[self.oio_pos]
            img_path = os.path.join(structure_folders[self.sf_pos], structure_folders[self.sf_pos].split('/')[-1])
            # print(img_path)

            if self.sf_pos == 0:  # for train
                json2labelImg(
                    'raw/json/' + str(i) + '.json',
                    img_path + '_' + seq_num + "_000019_gtFine_label" + output_type + ".png",
                    output_type)
            else:  # for instance image
                json2instanceImg(
                    'raw/json/' + str(i) + '.json',
                    img_path + '_' + seq_num + "_000019_gtFine_instance" + output_type + ".png",
                    output_type)


def _json_process(iter_num):
    json_path = "raw/json" + str(iter_num) + '.json'
    with open(json_path, "r", encoding="utf-8") as data_f:
        json_data = json.load(data_f)
        try:
            # 1st of del
            json_data.pop('imageData')
            json_data.pop('flags')
            json_data.pop('imagePath')
            json_data.pop('version')

            json_data['imgWidth'] = json_data.pop('imageWidth')
            json_data['imgHeight'] = json_data.pop('imageHeight')
            json_data['objects'] = json_data.pop('shapes')
            objs = json_data['objects']
            for obj in objs:
                obj.pop('flags')
                obj.pop('group_id')
                obj.pop('shape_type')

                obj['polygon'] = obj.pop('points')
                for point in obj['polygon']:
                    point[0] = int(point[0])
                    point[1] = int(point[1])
        except KeyError:
            logger.error('Some keys in the json file has been modified, formatting operation stopped.')
            return KeyError

    with open(json_path, 'w', newline='\n') as data_f:
        da = json.dumps(json_data, indent=4, sort_keys=True)
        data_f.write(da)


def generate_img():
    # TODO: self-determine to create multi thread jobs
    logger.info('Generating InstanceId and LabelId images...')
    global train_file_num, val_file_num

    # proThread = PercentageThread()
    train_label_thread = GenImgThread(0, 1, train_file_num, 0, 0)
    train_instance_thread = GenImgThread(1, 1, train_file_num, 0, 1)
    val_label_thread = GenImgThread(2, 1, val_file_num, 1, 0)
    val_instance_thread = GenImgThread(3, 1, val_file_num, 1, 1)

    train_label_thread.start()
    train_instance_thread.start()
    val_label_thread.start()
    val_instance_thread.start()

    train_instance_thread.join()
    train_label_thread.join()


def batch_rename():
    logger.info('Copying and Renaming json files...')
    # deal with original json files and original img (leftImg8bit)

    global train_file_num, val_file_num, train

    if (not os.path.exists(source_folder_names[1] + "/1.png")) \
            and os.path.exists(source_folder_names[1] + "/1.jpg"):  # TODO more precise
        logger.warning('JPG format image file detected, using Pillow to reformat')

        if TOTAL % 20 != 0:
            thread_num = int((TOTAL / 20)) + 1
        else:
            thread_num = (TOTAL / 20)

        for i in range(0, thread_num):
            cvtThread = CvtImgThread(i)
            cvtThread.start()

    try:
        logger.info('Copying and Renaming train files...')

        for i in range(1, TOTAL):

            if i in range(1, train_file_num):
                if i == 1:
                    logger.info('Handling train files...')
                seq_num = str(i).rjust(6, '0')
                shutil.copyfile(
                    "raw/json/" + str(i) + '.json',
                    os.path.join(
                        structure_folders[0],
                        structure_folders[0].split('/')[-1])
                    + seq_num + '_000019_gtFine_polygons.json')

                shutil.copyfile(
                    "raw/img/" + str(i) + '.png',
                    os.path.join(
                        structure_folders[2],
                        structure_folders[2].split('/')[-1])
                    + seq_num + '_000019_leftImg8bit.png'
                )
            elif i in range(train_file_num, train_file_num + val_file_num):
                if i == train_file_num:
                    print('\n')
                    logger.info('Handling validate files...')
                seq_num = str(i - train_file_num).rjust(6, '0')
                shutil.copyfile(
                    "raw/json/" + str(i) + '.json',
                    os.path.join(
                        structure_folders[1],
                        structure_folders[1].split('/')[-1])
                    + seq_num + '_000019_gtFine_polygons.json')

                shutil.copyfile(
                    "raw/img/" + str(i) + '.png',
                    os.path.join(
                        structure_folders[3],
                        structure_folders[3].split('/')[-1])
                    + seq_num + '_000019_leftImg8bit.png'
                )

    except FileNotFoundError as e:
        if e.errno == 2:
            logger.error("File not found: " + e.filename)
            return FileNotFoundError


def format_json():
    # dedicated to json files created by Labelme Application
    logger.info('Formatting json files...')
    skip = False

    with open('raw/json/1.json', "r", encoding="utf-8") as data_f:
        json_data = json.load(data_f)
        if "version" not in json_data and "imageData" not in json_data:
            logger.warning('Json files has been formatted before, skipping this process')
            skip = True

    if not skip:
        for i in range(1, TOTAL):
            _json_process(i)


def access_file():
    global train_file_num, val_file_num, check

    structure_folders.append(os.path.join("gtFine/train", city_names[0]))
    structure_folders.append(os.path.join("gtFine/val", city_names[1]))
    structure_folders.append(os.path.join("leftImg8bit/train", city_names[0]))
    structure_folders.append(os.path.join("leftImg8bit/val", city_names[1]))

    # print(structure_folders)

    for name in source_folder_names:
        if not os.path.exists(name):
            logger.error('{} folder is missing\nCheck your raw folders'.format(name))
            return FileNotFoundError

    # TODO check t_f_n and v_f_n aggregates to the numbers of all image files

    if train_file_num < 0 and val_file_num < 0:
        logger.error("Please modify 'train_file_num' and 'val_file_num' on the head of this file before running")
        return OSError
    logger.info("Current TRAIN file number: {}\tCurrent VAL file numbers: {}".format(train_file_num, val_file_num))

    for path in structure_folders:
        check = True
        if not os.path.exists(path):
            logger.warning(r'{} folder is missing'.format(path))
            check = False

    if not check:
        logger.info('Reconstructing folders now...')  # TODO hint beautify
        os.system('rm -rf gtFine')
        os.system('rm -rf leftImg8bit')

        for folder in structure_folders:
            os.makedirs(folder)
        logger.info('Reconstruction Finished')
    else:
        logger.info('Structure integrity check passed')


if __name__ == "__main__":
    access_file()
    format_json()
    generate_img()
    batch_rename()

    logger.info('Generating Completed!')
