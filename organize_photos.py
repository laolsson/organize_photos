
import os, sys

to_top_dir = ''

import Image

import os
import re
import sys
import time
import shutil

MONTHS=["Empty", "January", "February", "March", "April", "May",
        "June", "July", "August", "September", "October", "November", "December"]

CREATE_HARDLINK=0

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
    path, base = os.path.split(fn)
    print base # status
    prefix = get_exif_prefix(fn)
    if prefix is None:
        return 0
    if base.startswith(prefix):
        return 0 # file already renamed to this prefix

    year = prefix[0:4]
    month = prefix[5:7]
    month_str = MONTHS[int(month)]
    print year, month, month_str

    # create if it doesnt exist
    new_path_year = os.path.join(to_top_dir, year)
    new_path_total = os.path.join(new_path_year, year + "_" + month + "_" + month_str)
    if not os.path.exists(new_path_year):
        print "create", new_path_year
        os.mkdir(new_path_year)
    if not os.path.exists(new_path_total):
        print "create", new_path_total
        os.mkdir(new_path_total)

    new_name = prefix + '_' + base
    new_full_name = os.path.join(new_path_total, new_name)

    if CREATE_HARDLINK:
        print "hardline:", new_full_name
    else:
        try:
            print "copy:%s %s" % (fn, new_full_name)
            shutil.copyfile(fn, new_full_name)
        except Exception, e:
            print 'ERROR rename %s --> %s:%s' % (fn, new_full_name, e)
            return 0

    return 1


def rename_jpeg_files_in_dir(dn):
    print dn
    names = os.listdir(dn)
    count=0
    for n in names:
        file_path = os.path.join(dn, n)
        count += rename_jpeg_file(file_path)
    return count


if __name__ == '__main__':

    try:
        from_dir = sys.argv[1]
        to_top_dir = sys.argv[2]
    except:
        print "from_dir to_top_dir"
        sys.exit(1)

    print "from:%s to_top_dir:%s" %(from_dir, to_top_dir)

    from os.path import join, getsize
    for dir in os.listdir(from_dir):
        full_name = os.path.join(from_dir, dir)
        print dir, full_name
        rename_jpeg_files_in_dir(full_name)
