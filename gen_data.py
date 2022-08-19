import json
import os
import shutil

from PIL import Image
from cityscapesscripts.preparation.json2instanceImg import json2instanceImg
from cityscapesscripts.preparation.json2labelImg import json2labelImg
from loguru import logger

# ================ CONFIG ================ #

structure_folders = ['gtFine/train/aachen', 'gtFine/val/frankfurt',
                     'leftImg8bit/train/aachen', 'leftImg8bit/val/frankfurt']
folder_names = ['raw_train', 'raw_val']
city_names = ['aachen_', 'frankfurt_']
train_file_num = 0
val_file_num = 0
# 'r' stands for relative.
gtFine_paths = ["gtFine/train/aachen/", "gtFine/val/frankfurt/"]
r_path_lI8b_train = "leftImg8bit/train/aachen/"
r_path_lI8b_val = "leftImg8bit/val/frankfurt/"


# ================ CONFIG ================ #


def _gen_pic(type: int, i):
    #  0 for train; 1 for validate
    real_name = folder_names[type] + '/' + str(i + 1) + '.json'
    seq_num = str(i).rjust(6, '0')

    json2labelImg(
        real_name,
        gtFine_paths[type] + city_names[type] + seq_num + '_000019_gtFine_labelIds.png',
        'ids')
    json2instanceImg(
        real_name,
        gtFine_paths[type] + city_names[type] + seq_num + '_000019_gtFine_instanceIds.png',
        'ids')


def _cvt_jpg2png(path, num):
    for i in range(num):
        real_name = path + str(i + 1)
        logger.info('Processing ' + real_name)
        img = Image.open(real_name + '.jpg')
        img.save(real_name + '.png')
        os.remove(real_name + '.jpg')


def _json_process(path, num):
    for i in range(num):
        real_name = path + str(i + 1) + '.json'
        logger.info('Currently handling:' + real_name)

        with open(real_name, "r", encoding="utf-8") as data_f:
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

        with open(real_name, 'w', newline='\n') as data_f:
            da = json.dumps(json_data, indent=4, sort_keys=True)
            data_f.write(da)


def generate_img():
    logger.info('Generating InstanceId and LabelId images...')
    global train_file_num, val_file_num
    for i in range(train_file_num):
        _gen_pic(0, i)

    for i in range(val_file_num):
        _gen_pic(1, i)

    # TODO: this part could be modified into a multi-thread task


def batch_rename():
    logger.info('Copying and Renaming json files...')
    # deal with original json files and original img (leftImg8bit)

    global train_file_num, val_file_num
    try:
        logger.info('Copying and Renaming train files...')

        if (not os.path.exists("raw_train/1.png")) and os.path.exists("raw_train/1.jpg"):  # TODO more precise
            logger.warning('Jpg image file detected, using Pillow to reformat')
            _cvt_jpg2png('raw_train/', train_file_num)
            _cvt_jpg2png('raw_val/', val_file_num)

        for i in range(train_file_num):
            seq_num = str(i).rjust(6, '0')
            real_name = 'raw_train/' + str(i + 1)
            shutil.copyfile(real_name + '.json',
                            gtFine_paths[0] + 'aachen_' + seq_num + '_000019_gtFine_polygons.json')
            shutil.copyfile(real_name + '.png',
                            r_path_lI8b_train + 'aachen_' + seq_num + '_000019_leftImg8bit.png')

        logger.info('Copying and Renaming validate files...')
        for i in range(val_file_num):
            seq_num = str(i).rjust(6, '0')
            real_name = 'raw_val/' + str(i + 1)
            shutil.copyfile(real_name + '.json',
                            gtFine_paths[1] + 'frankfurt_' + seq_num + '_000019_gtFine_polygons.json')
            shutil.copyfile(real_name + '.png',
                            r_path_lI8b_val + 'frankfurt_' + seq_num + '_000019_leftImg8bit.png')
    except FileNotFoundError as e:
        if e.errno == 2:
            logger.error(
                "File not found")


def format_json():
    # dedicated to json files created by Labelme Application
    logger.info('Formatting json files...')
    skip = False

    with open('raw_train/1.json', "r", encoding="utf-8") as data_f:
        json_data = json.load(data_f)
        if "version" not in json_data and "imageData" not in json_data:
            logger.warning('Json files has been formatted before, skipping this process')
            skip = True

    if not skip:
        _json_process('raw_train/', train_file_num)
        _json_process('raw_val/', val_file_num)


def access_file():
    global train_file_num, val_file_num, check
    for name in folder_names:
        if not os.path.exists(name):
            logger.error('{} folder is missing\nCheck your raw folders'.format(name))
            return FileNotFoundError

    train_file_num = int(len(os.listdir('raw_train')) / 2)
    val_file_num = int(len(os.listdir('raw_val')) / 2)

    logger.info("Current TRAIN file number: {}\tCurrent VAL file numbers: {}".format(train_file_num, val_file_num))

    for path in structure_folders:
        check = True
        if not os.path.exists(path):
            logger.warning(r'{} folder is missing'.format(path))
            check = False

    if not check:
        logger.info('Reconstructing folders now...')
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
