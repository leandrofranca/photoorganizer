import argparse
from datetime import datetime
import imghdr
import os
import re


FILENAME_PATTERN_COM_HORA = ".*((19|20)\d{2})[\.\-_]?(0[1-9]|1[012])[\.\-_]?(0[1-9]|[12][0-9]|3[01])[\.\-_]?([0-1][0-9]|2[0-3])[\.\-_]?([0-5][0-9])[\.\-_]?([0-5][0-9])\d*[\-_]?.*\..*$"
FILENAME_PATTERN_SEM_HORA = ".*[\.\-_]((19|20)\d{2})[\.\-_]?(0[1-9]|1[012])[\.\-_]?(0[1-9]|[12][0-9]|3[01]).*"
FILE_FORMAT = '%Y-%m-%d-%H-%M-%S'
EXIF_FORMAT = '%Y:%m:%d %H:%M:%S'

def print_change(path):
    print("%(path)s changed." % {
        'path': os.path.abspath(path)
    })

def change_exif(path):
    dt = []
    m = re.search(FILENAME_PATTERN_COM_HORA, path)
    if m:
        dt.append(m.group(1))
        dt.append(m.group(3))
        dt.append(m.group(4))
        dt.append(m.group(5))
        dt.append(m.group(6))
        dt.append(m.group(7))
    else:
        m = re.search(FILENAME_PATTERN_SEM_HORA, path)
        if m:
            dt.append(m.group(1))
            dt.append(m.group(3))
            dt.append(m.group(4))
            dt.append('0')
            dt.append('0')
            dt.append('0')
    _datetime = datetime.strptime('-'.join(dt), FILE_FORMAT)
    exif_datetime = str(datetime.strftime(_datetime, EXIF_FORMAT))
    print("-overwrite_original_in_place")
    print("-AllDates=\"" + exif_datetime + "\"")
    title = str(path.split('\\')[-2])
    print("-ImageDescription=" + title)
    print(path)
    print("-execute")
    # print_change(path)

def needs_be_changed(file_path):
    return re.match(FILENAME_PATTERN_COM_HORA, file_path) or re.match(FILENAME_PATTERN_SEM_HORA, file_path)

def is_image(f):
    return os.path.isfile(f) and imghdr.what(f) in ['jpeg', 'gif', 'png']

def list_files(path, recursive):
    files = []
    for dirpath, dirs, filenames in os.walk(path):  # @UnusedVariable
        for f in filenames:
            full = os.path.join(dirpath, f)
            files.append(full)
        if not recursive:
            break
    return files

def change_files(directory, recursive):
    files = list_files(directory, recursive)
    image_files = list(filter(is_image, files))
    file_paths = list(map(os.path.abspath, image_files))
    file_paths = list(filter(needs_be_changed, file_paths))
    if file_paths:
        print("\"D:\\Exiftool\\exiftool.exe\" -stay_open 1 -@ -")
        changed_files = list(map(change_exif, file_paths))
        print("-stay_open")
        print("false")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Alter exifinfo from filename pattern.')
    parser.add_argument('-r', '--recursive', help='enable recursive renaming in subdirectories', action='store_true')
    parser.add_argument('-d', '--directory', help='directory of files to rename (defaults to .)', default='.')
    args = parser.parse_args()
    change_files(args.directory, args.recursive)
