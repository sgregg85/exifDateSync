import os
import time
from PIL import Image
from PIL.ExifTags import TAGS


def get_filenames(dir='null'):  # function to traverse the directory given and
                                # make a list of all .jpg and .jpeg files
    filenames = []
    if dir is 'null':   # if no directory passed, use the directory in which
                        # the script is located
        path = os.getcwd()
    else:
        path = dir
    for root, _, file in os.walk(path):     # outer loop traverses all files
                                                # in the folder provided and
                                                # subfolders
        for name in file:  # inner loop checks to see which files have jpg or
                            # jpeg as their extension and add those files to a
                            # list
            if name.lower().endswith(('jpg', 'jpeg')):
                filename = os.path.join(root, name)
                filenames.append(filename)

    return filenames    # return the list of images found


def get_exif(filename):     # function to read the exif data from an image and
                            # return the list
    exif_data = {}
    img = Image.open(filename)
    info = img._getexif()
    for key, value in info.items():
        decode_tags = TAGS.get(key, value)
        exif_data[decode_tags] = value
    return exif_data


def date_to_epoch(date): # change date/time values to epoch time
    date_format = '%Y:%m:%d %H:%M:%S'
    epoch = int(time.mktime(time.strptime(date, date_format)))
    return int(epoch)


def epoch_to_date(epoch): # change epoch values to readable date/time
    date = time.strftime('%Y:%m:%d %H:%M:%S', time.localtime(epoch))
    return date


file_write = open('log.txt', 'w')   # create file to write log
file_write.write("Files that were updated\n\n")
# prompt user for directory
directory = input("\nEnter the directory where the images are located.\n"
                  "Leave blank if the images are in the same folder as this "
                  "script\n")
if directory is "":     # if directory is blank, assign it the value of '.'
                        # which evaluates to the current folder
    directory = "."
# initiate list to store all files where the exif date were not found
files_without_data = []
files = get_filenames(directory)
for image in files:
    exif = get_exif(image)
    try:
        exif_date = exif['DateTimeOriginal'] # look for this exif tag
        stinfo = os.stat(image)  # read the file modified and file accessed
                                # date/time
        file_write.write(image + "\nModified date/time of file: " +
                         epoch_to_date(stinfo.st_mtime))
        file_write.write("\nExif date/time of file: " + exif_date)
        # check to see if the dates are the same
        if int(date_to_epoch(exif_date)) is int(stinfo.st_mtime):
            file_write.write("\nThe Exif date and the file modified date are"
                             " the same. No changes made\n\n")
        else:
            # set the file modified and file accessed date/time
            os.utime(image, (date_to_epoch(exif_date),
                             date_to_epoch(exif_date)))
            file_write.write("\nThe file modified date was synced to the Exif "
                             "date\n\n")
    except KeyError:
        files_without_data.append(image)


# after all files have been processed, write the list of files that could not
# be date synced to the log
file_write.write("\n\n\n\nFiles without EXIF data\n")
for items in files_without_data:
    file_write.write(items + '\n')

file_write.close()  # close the log
