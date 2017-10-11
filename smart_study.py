import json
import sys
import os
import urllib.request as request
course_api = 'http://sls.smartstudy.com/smartstudy_ustc/api/course/{}'
section_api="http://sls.smartstudy.com/smartstudy_ustc/api/course/{}/resource?itemId={}"
media_url='http://media6.smartstudy.com'

def check_dir(path):
    if not os.path.exists(path):
        os.mkdir(path)


course_id = sys.argv[1]
m3u8_dir = './' + course_id + '_m3u8_cache'
check_dir(m3u8_dir)
with request.urlopen(course_api.format(course_id)) as req:
    course_info = json.loads(req.read().decode())
for cid, course in course_info['data']['courses'].items():
    outline = course['outline']
    assert(course_id == str(course_info['data']['id']))
    basedir=os.path.join('./', course_info['data']['name'])
    check_dir(basedir)
    for chapter in outline:
        dir_p = os.path.join(basedir, chapter['name'])
        check_dir(dir_p)
        for section in chapter['section']:
            file_p = os.path.join(dir_p, section['name']+'.mp4')
            if os.path.exists(file_p):
                print('{} already exists, skip'.format(file_p), file=sys.stderr)
                continue
            section_id = section['id']
            section_api_request_url = section_api.format(course_id, section_id)
            with request.urlopen(section_api_request_url) as req:
                section_info = json.loads(req.read().decode())
            video_dest_dir = None
            for video_info in section_info['data']:
                if '高清' in video_info['type']:
                    video_dest_dir = media_url + video_info['dest']
                    break
            if video_dest_dir is None:
                print('{} doesn\'t have a HD source, skip'.format(file_p), file=sys.stderr)
            m3u8_request_url = video_dest_dir + '/dest.m3u8'
            with request.urlopen(m3u8_request_url) as req:
                m3u8_content = req.read().decode()
            m3u8_file_name = os.path.join(m3u8_dir,str(section_id)+'.m3u8')
            with open(m3u8_file_name, 'w') as m3u8_file:
                for line in m3u8_content.splitlines():
                    if line[0] != '#':
                        print(video_dest_dir + '/' + line, file=m3u8_file)
                    else:
                        print(line, file=m3u8_file)
            print('ffmpeg -protocol_whitelist "file,http,tcp" -i {} -c copy \'{}\''.format(m3u8_file_name, file_p))
