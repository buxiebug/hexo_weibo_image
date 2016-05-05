# encoding:utf8
__author__ = 'brianyang'

import os
import weibo_util
import sys
import re
import codecs
import json
import hashlib

reload(sys)
sys.setdefaultencoding('utf8')

base_dir = "/home/q/hexo/blog/source"
image_db = "/home/q/hexo/blog/image.db"

db_str = open(image_db, 'r').readline()
if db_str.strip() == "":
    db_str = "{}"
image_db_dict = json.loads(db_str)

os.system("rm -rf backup/_posts/")
os.system("cp -rf source/_posts backup/")
for i in os.listdir(base_dir + '/_posts'):
    path = base_dir + '/_posts/' + i
    print path
    lines = []
    with codecs.open(path, 'r') as f:
        for line in f.readlines():
            img_group = re.search(r"\[.*?\]\((.*?)\)", line)
            if img_group:
                for i in range(len(img_group.groups())):
                    img_str = img_group.groups(i + 1)[0].strip()
                    if str(img_str).startswith('/img'):
                        print img_str
                        m2 = hashlib.md5()
                        m2.update(open(base_dir + img_str).read())
                        image_md5 = m2.hexdigest()
                        print image_md5
                        if image_md5 not in image_db_dict:
                            image_url = weibo_util.get_image(base_dir + img_str)
                            if image_url == '':
                                continue
                            print image_url
                            image_db_dict[image_md5] = image_url
                        else:
                            image_url = image_db_dict.get(image_md5)
                        line = re.sub(img_str, image_url, line)
            lines.append(line)
    with open(path, 'w') as f:
        f.writelines(lines)

with open(image_db, 'w') as f:
    f.writelines(json.dumps(image_db_dict))

os.system('sh install.sh')
print "copy begin"
os.system('rm -rf source/_posts')
os.system('cp -rf backup/_posts source/')
print "copy done"
os.chdir("source/_posts")
print "注意下面的图片是否正确:"
os.system("ls | xargs cat| grep img ")
print 'done'





