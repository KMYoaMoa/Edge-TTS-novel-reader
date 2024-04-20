'''
prj : EDGE TTS Text2Speech for Windows
ref : https://github.com/rany2/edge-tts

aut : A. Kareno 2024/4/20
'''

import asyncio

import edge_tts # edgetts api

import tkinter as tk
from tkinter import filedialog

import time

import os

# The chosen voice of edge tts. Variable.
VOICE = "zh-CN-XiaoxiaoNeural"

def text_split(file_path): # File split by GPT3.5

    # Read text file with utf-8

    with open(file_path, 'r', encoding = 'utf-8') as file:
        # split by endline
        lines = file.read().split('\n')

    # Longest chunk under 5000 words. 

    '''
    The number is variable.
    The smaller, the faster the tts processing speed for single file when creating more temporary files.
    But the total storage size doesn't change.
    Proper value might influence the overall efficiency.
    According to a limited number of tests, 5000 takes about 40 secs to generate 180k words, fast enough and stable.
    '''

    current_chunk = ''
    processed_lines = []
    for line in lines:
        if len(current_chunk) + len(line) <= 5000:
            current_chunk += line + ' '
        else:
            processed_lines.append(current_chunk)
            current_chunk = line + ' '
    
    # The last chunk
    if current_chunk:
        processed_lines.append(current_chunk)

    return processed_lines

async def amain(text, voice, output_file) -> None: # async task
    print('MSG : tts processing ' + output_file + ' split...')
    retry_cnt = 0
    success_flag = False
    communicate = edge_tts.Communicate(text, voice)
    while retry_cnt <= 3 and success_flag == False:
        try:
            await communicate.save(output_file)
        except Exception as e:
            print("* ERR : ", e.value, ' WHEN TTS PROCESSING ' + output_file + ' SPLIT =( ')
            print('* MSG : RETRYING ', retry_cnt, '/3 TIMES')
            retry_cnt += 1
        else :
            success_flag = True
    if success_flag :
        print('MSG : tts ' + output_file + ' ok')
    else :
        print('*** ERR : RETRY TOO MUCH TIMES. PROCESS FAILED.')
        os.system('pause')
        exit()

def task_list_generator() :
    n = 0
    while n < len(processed_text_list):
        task_element = [amain(processed_text_list[i], VOICE, 'tmp' + str(i) + '.mp3') for i in range(n, min(n + 32, len(processed_text_list)))]
        yield task_element
        n += 32

def runEventLoop(): # event loop of tasks
    generator = task_list_generator()
    for task_ele in generator :
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(asyncio.wait(task_ele))
        loop.close()

if __name__ == "__main__":
    
    # Text file selection
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()
    
    # Timer
    t1 = time.time()

    # Text file split
    try:
        processed_text_list = text_split(file_path)
    except Exception as e:
        print("ERR : ", e, ' WHEN SPLITING TEXT =( ')
        os.system('pause')
        exit()
    
    # Run task loop
    loop = asyncio.get_event_loop()
    runEventLoop()
    asyncio.set_event_loop(loop)

    # Joint .mp3 files

    command = 'copy /b '
    for i in range(len(processed_text_list)) :
        command += 'tmp' + str(i) + '.mp3+'
    command = command[:-1:] + ' output_file.mp3'

    os.system(command)
    os.system('del tmp*.mp3')

    # Finish
    t2 = time.time()

    print('MSG : OK! Your .txt file has turned into an MP3 file in amazing', t2 - t1, 'seconds! \nFind output_file.mp3 and enjoy your time!')
    os.system('pause')