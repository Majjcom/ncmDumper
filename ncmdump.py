# -*- coding: utf-8 -*-
import threading
import binascii
import struct
import base64
import json
import time
import os
from Crypto.Cipher import AES
# pip install pycryptodome

def dump(file_path):
    #十六进制转字符串
    core_key = binascii.a2b_hex("687A4852416D736F356B496E62617857")
    meta_key = binascii.a2b_hex("2331346C6A6B5F215C5D2630553C2728")
    unpad = lambda s: s[0:-(s[-1] if type(s[-1]) == int else ord(s[-1]))]
    f = open(file_path, 'rb')
    header = f.read(8)
    #字符串转十六进制
    assert binascii.b2a_hex(header) == b'4354454e4644414d'
    f.seek(2,1)
    key_length = f.read(4)
    key_length = struct.unpack('<I', bytes(key_length))[0]
    key_data = f.read(key_length)
    key_data_array = bytearray(key_data)
    for i in range(0, len(key_data_array)):
        key_data_array[i] ^= 0x64
    key_data = bytes(key_data_array)
    cryptor = AES.new(core_key, AES.MODE_ECB)
    key_data = unpad(cryptor.decrypt(key_data))[17:]
    key_length = len(key_data)
    key_data = bytearray(key_data)
    key_box = bytearray(range(256))
    c = 0
    last_byte = 0
    key_offset = 0
    for i in range(256):
        swap = key_box[i]
        c = (swap + last_byte + key_data[key_offset]) & 0xff
        key_offset += 1
        if key_offset >= key_length:
            key_offset = 0
        key_box[i] = key_box[c]
        key_box[c] = swap
        last_byte = c
    meta_length = f.read(4)
    meta_length = struct.unpack('<I', bytes(meta_length))[0]
    meta_data = f.read(meta_length)
    meta_data_array = bytearray(meta_data)
    for i in range(0, len(meta_data_array)):
        meta_data_array[i] ^= 0x63
    meta_data = bytes(meta_data_array)
    meta_data = base64.b64decode(meta_data[22:])
    cryptor = AES.new(meta_key, AES.MODE_ECB)
    meta_data = unpad(cryptor.decrypt(meta_data)).decode('utf-8')[6:]
    meta_data = json.loads(meta_data)
    crc32 = f.read(4)
    crc32 = struct.unpack('<I', bytes(crc32))[0]
    f.seek(5, 1)
    image_size = f.read(4)
    image_size = struct.unpack('<I', bytes(image_size))[0]
    image_data = f.read(image_size)
    # file_name = f.name.split("/")[-1].split(".ncm")[0] + '.' + meta_data['format']
    file_name = os.path.splitext(os.path.split(f.name)[1])[0] + '.' + meta_data['format']
    m = open(os.path.join(os.getcwd(), 'unlock/' + file_name), 'wb')
    chunk = bytearray()
    while True:
        chunk = bytearray(f.read(0x8000))
        chunk_length = len(chunk)
        if not chunk:
            break
        for i in range(1, chunk_length+1):
            j = i & 0xff
            chunk[i-1] ^= key_box[(key_box[j] + key_box[(key_box[j] + j) & 0xff]) & 0xff]
        m.write(chunk)
    m.close()
    f.close()
    return file_name


class dumper(threading.Thread):
    def __init__(self, fpath, basket):
        super().__init__()
        self._fpath = fpath
        self._basket = basket
    
    def run(self):
        try:
            dump(self._fpath)
        except:
            pass
        finally:
            self._basket[self._fpath] = 2


def upperPrint(s: str):
    column = os.get_terminal_size().columns
    print('\r' + ' ' * (column - 1), end='', flush=True)
    print('\r' + s, flush=True)


def printBar(now:int, total:int, threads:int):
    size = os.get_terminal_size()
    size_columns = size.columns - 1
    text_end = '  threads:{}  {}/{}'.format(threads, now, total)
    percent:float = now / total
    bar_size = size_columns - len(text_end)
    bar_text_end = ']{}%/100%'.format(round(percent * 100, 2))
    bar_len = bar_size - len(bar_text_end) - 1
    bar_text_main = ''
    for i in range(int(bar_len * percent)):
        if i == int(bar_len * percent) - 1:
            bar_text_main += '>'
        else:
            bar_text_main += '='
    for i in range(bar_len - int(bar_len * percent)):
        bar_text_main += ' '
    bar_text = '\r[{}{}{}'.format(bar_text_main, bar_text_end, text_end)
    print(bar_text, end='', flush=True)


if __name__ == '__main__':
    if not os.path.exists('./unlock'):
        os.mkdir('./unlock')
    dirs = os.listdir()
    musicFiles = dict()
    for i in dirs:
        if os.path.isfile(i):
            if os.path.splitext(i)[1] == '.ncm':
                musicFiles[os.path.abspath(i)] = 0
    totalCount = len(musicFiles)
    process = [0, 0, 0]
    while True:
        count = 0
        tmp = None
        for key in musicFiles:
            if musicFiles[key] == 1:
                count += 1
            if count < 5 and musicFiles[key] == 0:
                upperPrint('解密中...\t{}'.format(key))
                musicFiles[key] = 1
                tmp = dumper(key, musicFiles)
                tmp.start()
                count += 1
        fcount = 0
        for key in musicFiles:
            if musicFiles[key] == 2:
                fcount += 1
        process[0], process[1], process[2] = fcount, totalCount, count
        printBar(fcount, totalCount, count)
        if fcount == totalCount:
            break
        time.sleep(0.5)
        
    print('\n\033[32m解密完成，存放在unlock目录中\033[0m')
    input('按下回车继续...')
