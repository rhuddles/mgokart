# Renames image files from a director at '../conez' to something helpful

import os

IMG_DIR = "../conez/"
BASENAME = "conez"
count = 0

for image in sorted(os.listdir(IMG_DIR)):
    os.rename(IMG_DIR + image, IMG_DIR + BASENAME + '%03d' % count + '.png')
    count += 1
