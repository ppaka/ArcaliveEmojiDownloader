import requests
from bs4 import BeautifulSoup
import os
import imageio
import os

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
    for i,im in enumerate(reader):
        writer.append_data(im)
    writer.close()

print('---- 깃허브: https://github.com/ppaka ----')

path = os.path.dirname(os.path.abspath(__file__))
url = input('아카콘 페이지 주소 입력: ')

req = requests.get(url)
soup = BeautifulSoup(req.text, "html.parser")

title_element = soup.select_one(
    'body > div > div.content-wrapper.clearfix > article > div > div.article-wrapper > div.article-head > div.title-row > div')
title = str(title_element).splitlines()
title = title[1]
print('다음을 다운로드합니다...', title)

element = soup.select_one(
    'body > div > div.content-wrapper.clearfix > article > div > div.article-wrapper > div.article-body > div')

splited = str(element).splitlines()
if splited[0] == '<div class="emoticons-wrapper">':
    splited.pop(0)
    splited.pop(len(splited)-1)
    for i in range(len(splited)):
        splited[i] = splited[i].replace('<img loading="lazy" src="', '')
        splited[i] = splited[i].replace('"/>', '')

        splited[i] = splited[i].replace(
            '<video autoplay="" loading="lazy" loop="" muted="" playsinline="" src="', '')
        splited[i] = splited[i].replace('"></video>', '')
        splited[i] = 'https:'+splited[i]

data = element

count = 0

for i in splited:
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

print('다운로드를 마쳤습니다')
