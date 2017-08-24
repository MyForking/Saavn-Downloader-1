#!/usr/bin/python

from bs4 import BeautifulSoup
import os
import requests
from json import JSONDecoder
import base64
import wget

from pyDes import *

try:
    input = raw_input
except NameError:
    pass

proxy_ip = ''
# set http_proxy from environment
if('http_proxy' in os.environ):
    proxy_ip = os.environ['http_proxy']

proxies = {
  'http': proxy_ip,
  'https': proxy_ip,
}
# proxy setup end here

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0'
}
base_url = 'http://h.saavncdn.com'
json_decoder = JSONDecoder()

# Key and IV are coded in plaintext in the app when decompiled
# and its pretty insecure to decrypt urls to the mp3 at the client side
# these operations should be performed at the server side.
des_cipher = des(b"38346591", ECB, b"\0\0\0\0\0\0\0\0" , pad=None, padmode=PAD_PKCS5)
    

def downloader_saavn(input_url):
    try:
        res = requests.get(input_url, proxies=proxies, headers=headers)
    except Exception as e:
        print('Error accessing website error: '+e)
        sys.exit()


    soup = BeautifulSoup(res.text,"lxml")

    # Encrypted url to the mp3 are stored in the webpage
    songs_json = soup.find_all('div',{'class':'hide song-json'})

    currentDirectory = os.path.join(os.getcwd(), "downloads")
    
    for song in songs_json:
        obj = json_decoder.decode(song.text)
        print(obj['album'],'-',obj['title'])
        enc_url = base64.b64decode(obj['url'].strip())
        dec_url = des_cipher.decrypt(enc_url,padmode=PAD_PKCS5).decode('utf-8')
        dec_url = base_url + dec_url.replace('mp3:audios','') + '.mp3'
        #print(dec_url,'\n')
        fileExistsName = os.path.join(currentDirectory, obj['title']+".mp3")
        if os.path.exists(fileExistsName):
            continue
        else:
            #wget.download(dec_url, obj['title']+".mp3")
            pass

    for fileName in os.listdir(os.getcwd()):
        if fileName.endswith(".mp3"):
            sourceFile = os.path.join(os.getcwd(), fileName)
            destinationFile = os.path.join(currentDirectory, fileName)
            os.rename(sourceFile, destinationFile)

if __name__ == "__main__":
    loop = True
    while(loop):
        input_url = input('Enter the song url:').strip()

        if 'search' in input_url:
            try:
                res = requests.get(input_url, proxies=proxies, headers=headers)
            except Exception as e:
                print('Error accessing website error: '+e)
                sys.exit()

            soup = BeautifulSoup(res.text,"lxml")
            for a in soup.select('span.title a[href]'):
                downloader_saavn(a['href'].strip())
        else:
            downloader_saavn(input_url)

        continueDownload = input('Do you want to continue downloading? (y/n):').strip()
        if continueDownload == 'y':
            loop = True
        else:
            loop = False