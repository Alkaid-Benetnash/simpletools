import json
import os
import sys
import urllib.request

def check_dir(path):
    if not os.path.exists(path):
        os.mkdir(path)
if len(sys.argv) < 4:
    print("fname, url template, count")
    sys.exit(-1)
fname = sys.argv[1]
dirname = fname + '.d'
listpath = os.path.join(dirname, fname + '.list')
dstname = fname + '.pts'
url_template = sys.argv[2]
count = int(sys.argv[3])
check_dir(dirname)
d = open(listpath,'w')
for i in range(count):
    p = str(i)+'.pts'
    if not os.path.exists(p):
        url = url_template + '_{}_{}.pts'.format(i, count)
        print('wget -nc --timeout=2 \'{}\' -O \'{}\''.format(url, p), file=d)
d.close()
