# photoorganizer

Rename image files based on the EXIF DateTimeOriginal, DateTimeDigitized or DateTime field.
All images in the specified folder(s) are renamed following the format `IMG_YYYYMMDD_hhmmss.ext`, based on when it was taken.

Images without the field set, or without EXIF data altogether, are ignored.
Should multiple images have the same DateTimeOriginal, DateTimeDigitized or DateTime values, the script will generate a postfix to append to the filename.

### Usage

    renamer [-h] [-r] [-d DIRECTORY]

    Rename image files based on the EXIF DateTimeOriginal, DateTimeDigitized or DateTime field.

    optional arguments:
        -h, --help                show this help message and exit
        -r, --recursive           enable recursive renaming in subdirectories
        -d DIRECTORY,             directory of files to rename (defaults to .)
         --directory DIRECTORY