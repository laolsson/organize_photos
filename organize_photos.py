
import os, sys

to_top_dir = ''

from PIL import Image

import os
import re
import sys
import time
import shutil

MONTHS=["Empty", "January", "February", "March", "April", "May",
        "June", "July", "August", "September", "October", "November", "December"]


def extract_jpeg_exif_time(jpegfn):
    if not os.path.isfile(jpegfn):
        return None
    try:
        im = Image.open(jpegfn)
        if hasattr(im, '_getexif'):
            exifdata = im._getexif()
            ctime = exifdata[0x9003]
            #print ctime
            return ctime
    except:
        _type, value, traceback = sys.exc_info()
        print "Error:\n%r", value

    return None


def get_exif_prefix(jpegfn):
    ctime = extract_jpeg_exif_time(jpegfn)
    if ctime is None:
        return None
    ctime = ctime.replace(':', '_')
    ctime = re.sub('[^\d]+', '_', ctime)
    return ctime


def rename_jpeg_file(fn):
    if not os.path.isfile(fn):
        return 0
    ext = os.path.splitext(fn)[1].lower()
    if ext not in ['.jpg', '.jpeg', '.jfif']:
        return 0
    path, fname = os.path.split(fn)
    prefix = get_exif_prefix(fn)
    if prefix is None:
        print 'No EXIF found for ', fn, ' not copying'
        return 0

    year = prefix[0:4]
    month = prefix[5:7]
    month_str = MONTHS[int(month)]

    # create if it doesnt exist
    new_path_year = os.path.join(to_top_dir, year)
    new_path_total = os.path.join(new_path_year, year + "_" + month + "_" + month_str)
    if not os.path.exists(new_path_year):
        print "create", new_path_year
        os.mkdir(new_path_year)
    if not os.path.exists(new_path_total):
        print "create", new_path_total
        os.mkdir(new_path_total)

    # Only add the date part of the name if it doesn't already have it
    if not fname.startswith(prefix):
        fname = prefix + '_' + fname
    new_full_name = os.path.join(new_path_total, fname)

    try:
        print "copy:%s %s" % (fn, new_full_name)
        shutil.copyfile(fn, new_full_name)
    except Exception, e:
        print 'ERROR rename %s --> %s:%s' % (fn, new_full_name, e)
        return 0

    return 1


def step(files, dirname, names):
    for name in names:
        if name.lower().endswith('jpg') or name.lower().endswith('png'):
            rename_jpeg_file(dirname + '/' + name)


# Recursively find all images in the top_dir and rename and copy the to
def process_files_in_dir(top_dir):
    from os import listdir
    from os.path import isfile, join
    files = []
    os.path.walk(top_dir, step, files)


if __name__ == '__main__':
    global to_top_dir

    try:
        from_dir = sys.argv[1]
        to_top_dir = sys.argv[2]
    except:
        print "organize_photos.py from_dir to_top_dir"
        sys.exit(1)
    print "from:%s to_top_dir:%s" %(from_dir, to_top_dir)
    print process_files_in_dir(from_dir)
