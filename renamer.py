import argparse
from datetime import datetime
import imghdr
import os
import re

from PIL import Image
from PIL.ExifTags import TAGS

MOCK = True

EXIF_FORMAT = '%Y:%m:%d %H:%M:%S'
FILE_DATE_FORMAT = '%Y%m%d_%H%M%S'

FILENAME_PATTERN = "(\d{2,4}[\.\-_]?\d{2}[\.\-_]?\d{2}[\.\-_]?\d{2}[\.\-_]?\d{2}[\.\-_]?\d{2}\d*)[-_]?(.*)(\..*)$"

def get_exif(file_path):
    ret = {}
    i = Image.open(file_path)
    info = i._getexif()
    for tag, value in info.items():
        decoded = TAGS.get(tag, tag)
        ret[decoded] = value
    return ret

def file_date_format(date):
    return str(datetime.strftime(date, FILE_DATE_FORMAT))

def convert_date(_str):
    return datetime.strptime(_str, EXIF_FORMAT)

def rename_files(directory, recursive):
    files = list_files(directory, recursive)
    image_files = list(filter(is_image, files))
    old_paths = list(map(os.path.abspath, image_files))
    old_paths = list(filter(needs_renaming, old_paths))
    if old_paths:
        new_paths = list(map(create_new_path, old_paths))
        pairs = list(zip(old_paths, new_paths))
        pairs = [x_y for x_y in pairs if x_y[0] != x_y[1]]
        total = len(list(map(rename, pairs)))
        print("%d pictures renamed" % total)

def list_files(path, recursive):
    files = []
    for dirpath, dirs, filenames in os.walk(path):  # @UnusedVariable
        for f in filenames:
            full = os.path.join(dirpath, f)
            files.append(full)
        if not recursive:
            break
    return files

def is_image(f):
    return os.path.isfile(f) and imghdr.what(f) in ['jpeg', 'gif', 'png']

def needs_renaming(file_path):
    return not re.match(".*" + FILENAME_PATTERN, file_path)

def create_new_path(old_path):
    dirname = os.path.dirname(old_path)
    try:
        time_taken = get_filename_date_time_exif(old_path)
    except Exception:
        return old_path
    name = 'IMG_' + time_taken
    ext = os.path.splitext(old_path)[1].lower()
    return os.path.join(dirname, name + ext)

def get_filename_date_time_exif(file_path):
    exif_info = get_exif(file_path)
    date_time = None
    try:
        date_time = convert_date(exif_info['DateTimeOriginal'])
    except:
        try:
            date_time = convert_date(exif_info['DateTimeDigitized'])
        except:
            date_time = convert_date(exif_info['DateTime'])

    return file_date_format(date_time)

def rename(pair):
    old, new = pair
    while os.path.exists(new):
        # postfix = prompt_postfix(new)
        postfix = suggest_postfix(new)
        new = set_file_postfix(new, postfix)
    if MOCK == False:
        os.rename(old, new)
    print_change(old, new)

def set_file_postfix(file_path, postfix):
    def substitute_postfix(m):
        return m.group(1) + "-" + postfix + m.group(3)
    return re.sub(FILENAME_PATTERN, substitute_postfix, file_path)

def prompt_postfix(file_path):
    default = suggest_postfix(file_path)
    print("!! Name in use:", file_path)
    postfix = input("!! Please specify a postfix [%s]: " % default)
    if not postfix:
        return default
    return postfix

def suggest_postfix(file_path):
    import itertools
    for i in itertools.count():
        if not os.path.exists(set_file_postfix(file_path, str(i))):
            return str(i)

def print_change(old, new):
    print("%(dir)s\n  %(from)s -> %(to)s\n" % {
        'dir': os.path.dirname(os.path.commonprefix((old, new))),
        'from': os.path.basename(old),
        'to': os.path.basename(new)
    })

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Rename image files based on the EXIF DateTimeOriginal, DateTimeDigitized or DateTime field.')
    parser.add_argument('-r', '--recursive', help='enable recursive renaming in subdirectories', action='store_true')
    parser.add_argument('-d', '--directory', help='directory of files to rename (defaults to .)', default='.')
    args = parser.parse_args()
    rename_files(args.directory, args.recursive)
