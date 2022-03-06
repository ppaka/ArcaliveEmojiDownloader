import requests
import bs4
import os
import imageio
import sys
import re
import ffmpeg
import imageio_ffmpeg

def download(url: str, file_name):
    with open(file_name, "wb") as file:
        response = requests.get(url)
        file.write(response.content)


def cfDecodeEmail(encodedString):
    r = int(encodedString[:2],16)
    email = ''.join([chr(int(encodedString[i:i+2], 16) ^ r) for i in range(2, len(encodedString), 2)])
    return email


def convertFile(inputpath, outputdir, palettedir,outputfilename):
    outputpath = outputdir + outputfilename + '.gif'
    palettepath = palettedir + outputfilename+'_palette.png'

    reader = imageio.get_reader(inputpath)
    fps = reader.get_meta_data()['fps']

    # print('원본 fps: ' + str(fps))
    while fps>50:
        fps = fps/2
        # print('조정 fps: ' + str(fps))

    ffmpeg.input(inputpath).filter(filter_name='palettegen').output(palettepath, loglevel='error').global_args('-hide_banner').overwrite_output().run(cmd=imageio_ffmpeg.get_ffmpeg_exe())
    ffmpeg.filter([ffmpeg.input(inputpath), ffmpeg.input(palettepath)], filter_name='paletteuse').output(outputpath, r=fps, loglevel='error').global_args('-hide_banner').overwrite_output().run(cmd=imageio_ffmpeg.get_ffmpeg_exe())
    # outputpath = outputdir + outputfilename + '.gif'

    # reader = imageio.get_reader(inputpath)
    # fps = reader.get_meta_data()['fps']

    # writer = imageio.get_writer(outputpath, fps=fps)
    # for i, im in enumerate(reader):
    #     writer.append_data(im)
    # writer.close()

def main():
    if getattr(sys, 'frozen', False):
        dir = os.path.dirname(os.path.abspath(sys.executable))
    else:
        dir = os.path.dirname(os.path.abspath(__file__))

    print('---- 깃허브: https://github.com/ppaka/ArcaliveEmojiDownloader ----')
    try:
        v_req = requests.get("https://raw.githubusercontent.com/ppaka/ArcaliveEmojiDownloader/master/version.txt")
        internet_version = int(v_req.text)
        local_version = int(open(dir+'\\version.txt').readline())

        if local_version < internet_version:
            print('업데이트가 있습니다! 깃허브에서 최신 버전을 내려받아주세요!')
        else: print('최신버전입니다!')
    except:
        print('업데이트 확인에 실패했습니다...')
    
    url = input('\n아카콘 페이지 주소 입력: ')

    req = requests.get(url)
    soup = bs4.BeautifulSoup(req.text, "html.parser")

    title_element = soup.select_one(
        'body > div.root-container > div.content-wrapper.clearfix > article > div > div.article-wrapper > div.article-head > div.title-row > div')

    title = str(title_element).splitlines()[1]
    
    if '<a class="__cf_email__"' in title:
        print('제목에 암호화된 기호가 있습니다. 변환 작업을 진행합니다.')
        start_index = title.find('<a class="__cf_email__"')
        end_index = title.find('</a>')+4
        
        email_source = title[start_index:end_index]

        value_start_index = email_source.find('data-cfemail="')+14
        value_end_index = email_source.find('" href="/cdn-cgi/l/email-protection">')

        endcoded_str = email_source[value_start_index:value_end_index]
        email = cfDecodeEmail(endcoded_str)

        title = title[:start_index] + email + title[end_index:]

    if title.endswith(' ') or title.startswith(' '):
        print('제목 맨 끝에 공백이 존재합니다. 공백을 제거합니다.')
        title.strip()

    print('다음을 다운로드합니다...', '"'+title+'"')

    if re.search('[\/:*?"<>|]', title):
        old_title = title
        title = re.sub('[\/:*?"<>|]', '', title)
        print(f'제목에 사용 불가능한 문자가 있어 폴더이름을 변경하여 저장합니다.\n{old_title} ▶▶ {title}')

    element = soup.select_one(
        'body > div > div.content-wrapper.clearfix > article > div > div.article-wrapper > div.article-body > div')

    total_count = 0

    for i in element.find_all('video'):
        total_count+=1
        #print(i['src'])
    for i in element.find_all('img'):
        total_count+=1
        #print(i['src'])

    print('찾은 아카콘 개수: ' + str(total_count))

    arcacon = []

    for i in element.children:
        if type(i) == bs4.element.Tag:
            if str(i).startswith('<div'):
                break
            arcacon.append('https:'+str(i['src']))

    count = 0

    for i in arcacon:
        count += 1
        sav_dir = dir.replace('\\', '/')+'/'+title+'/'

        if not os.path.exists(sav_dir):
            os.makedirs(sav_dir)

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

            vid_dir = sav_dir+'/videos/'
            if not os.path.exists(vid_dir):
                os.makedirs(vid_dir)

            palette_dir = sav_dir+'/palette/'
            if not os.path.exists(palette_dir):
                os.makedirs(palette_dir)
                
            download(i, vid_dir+filename)
            convertFile(vid_dir+filename, sav_dir, palette_dir, str(count))

    print('---- 다운로드를 마쳤습니다 ----')
    os.system("pause")

if __name__=='__main__':
    main()