import requests
from bs4 import BeautifulSoup
import os
import imageio
import os
import re


def download(url: str, file_name):
    with open(file_name, "wb") as file:
        response = requests.get(url)
        file.write(response.content)


class TargetFormat(object):
    GIF = ".gif"
    MP4 = ".mp4"
    AVI = ".avi"


def convertFile(inputpath, outputdir, outputfilename, targetFormat):
    outputpath = outputdir + outputfilename + targetFormat

    reader = imageio.get_reader(inputpath)
    fps = reader.get_meta_data()['fps']

    writer = imageio.get_writer(outputpath, fps=fps)
    for i, im in enumerate(reader):
        writer.append_data(im)
    writer.close()


print('---- 깃허브: https://github.com/ppaka/ArcaliveEmojiDownloader ----')

path = os.path.dirname(os.path.abspath(__file__))
url = input('아카콘 페이지 주소 입력: ')

req = requests.get(url)
soup = BeautifulSoup(req.text, "html.parser")

title_element = soup.select_one(
    'body > div > div.content-wrapper.clearfix > article > div > div.article-wrapper > div.article-head > div.title-row > div')
title = str(title_element).splitlines()
title = title[1]

while True:
    if title.endswith(' '):
        print('제목 맨 끝에 공백이 존재합니다. 공백을 제거합니다.')
        title = title[0:-1]
    else:
        break
print('다음을 다운로드합니다...', '"'+title+'"')

if re.search('[\/:*?"<>|]', title):
    old_title = title
    title = re.sub('[\/:*?"<>|]', '', title)
    print(f'제목에 사용 불가능한 문자가 있어 폴더이름을 변경하여 저장합니다.\n{old_title} ▶▶ {title}')

element = soup.select_one(
    'body > div > div.content-wrapper.clearfix > article > div > div.article-wrapper > div.article-body > div')

arcacon = str(element).splitlines()
if arcacon[0] == '<div class="emoticons-wrapper">':
    arcacon.pop(0)
    arcacon.pop(len(arcacon)-1)
    for i in range(len(arcacon)):
        arcacon[i] = arcacon[i].replace('<img loading="lazy" src="', '')
        arcacon[i] = arcacon[i].replace('"/>', '')

        arcacon[i] = arcacon[i].replace(
            '<video autoplay="" loading="lazy" loop="" muted="" playsinline="" src="', '')
        arcacon[i] = arcacon[i].replace('"></video>', '')
        arcacon[i] = 'https:'+arcacon[i]

count = 0

for i in arcacon:
    count += 1
    sav_dir = path.replace('\\', '/')+'/'+title+'/'

    if not os.path.exists(sav_dir):
        os.makedirs(sav_dir)

    vid_dir = sav_dir+'/videos/'
    if not os.path.exists(vid_dir):
        os.makedirs(vid_dir)

    filename = str(count)
    if i.endswith('.png'):
        filename += '.png'
        download(i, sav_dir+filename)
    elif i.endswith('.jpeg'):
        filename += '.jpeg'
        download(i, sav_dir+filename)
    elif i.endswith('.jpg'):
        filename += '.jpg'
        download(i, sav_dir+filename)
    elif i.endswith('.gif'):
        filename += '.gif'
        download(i, sav_dir+filename)
    elif i.endswith('.mp4'):
        filename += '.mp4'
        download(i, vid_dir+filename)
        convertFile(vid_dir+filename, sav_dir, str(count), TargetFormat.GIF)

print('----다운로드를 마쳤습니다----')
