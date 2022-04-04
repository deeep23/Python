import csv
import datetime
import time
import os
import urllib.request
from pydub import AudioSegment
import traceback
from playsound import playsound
import pandas as pd
import ssl
import pydub
ssl._create_default_https_context = ssl._create_unverified_context
file1 = open("output.txt", "a", encoding='utf8')
take_inputs = True


# pydub.AudioSegment.ffmpeg = "C:/Users/obscu/Downloads/ffmpeg-4.4-full_build/ffmpeg-4.4-full_build/bin/ffmpeg"  #changes
#sound = AudioSegment.from_mp3("audio.mp3")

def start_playing(filename, keyword, clip_size, last):
    if filename != "":
        # AudioSegment.converter = 'C:/Users/obscu/Downloads/ffmpeg-4.4-full_build/ffmpeg-4.4-full_build/bin/ffmpeg' #changes
        channel = 2 #changes
        with open(filename, encoding='utf8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            listen = 0
            for row in csv_reader:
                # skip headers
                if line_count == 0:
                    line_count += 1
                    continue
                else:
                    line_count += 1
                    if row[0].strip() != keyword or line_count in range(last+1):  #changes
                        continue
                    # FOR UTC
                    call_start_time = datetime.datetime.fromtimestamp((int(str(row[2]).split("-")[0]) - 19800000) / 1e3)

                    # for IST
                    # call_start_time = datetime.datetime.fromtimestamp((int(str(row[2]).split("-")[0])) / 1e3)
                    transcript_end_time = datetime.datetime.strptime(row[3], '%Y-%m-%dT%H:%M:%S.%fZ')
                    # transcript_end_time = datetime.datetime.strptime(row[3], '%d/%m/%Y %H:%M:%S')
                    # print(row)
                    transcript_received_seconds = (transcript_end_time - call_start_time).total_seconds()
                    #transcript_received_seconds = float(row[4])
                    start_pos = 0
                    if (transcript_received_seconds - clip_size) > 0:
                        start_pos = transcript_received_seconds - clip_size

                    try:
                        print("URL-> " + row[1])

                        if row[1].split(".")[-1] == 'wav':   # changes
                            urllib.request.urlretrieve(row[1], 'audio.wav')
                            audio = AudioSegment.from_wav('audio.wav')
                        os.remove('audio.wav')
                        # Listen to single channel only
                        if channel == 2:
                            if audio.channels > 1:
                                mono_audios = audio.split_to_mono()
                                # customer - 1
                                # agent - 2
                                mono_left = mono_audios[1]
                                audio = mono_left
                        audio = audio[start_pos * 1000:transcript_received_seconds * 1000 + clip_size*1000]
                        print(str(line_count) + ': Playing for keyword ' + keyword)
                        # playsound(audio)
                        audio.export('file//audio-extract' + str(line_count) + '.wav', format="wav")
                        playsound('file//audio-extract' + str(line_count) + '.wav')
                        listen+=1
                        print(listen)
                        # time.sleep(transcript_received_seconds - start_pos)
                        # os.remove('audio-extract' + str(line_count) + '.wav')
                        # subprocess.Popen(['mpg123', '-q', 'audio.wav']).wait()
                        # if take_inputs:
                        #     print("Observation ?")
                        #     case = ""
                        #     file1.write(keyword + "~" + row[2] + "~" + case + '\n')
                        #     file1.flush()

                    except Exception as e:
                        traceback.print_exc()
            print(f'Processed {line_count} lines.')


if __name__ == "__main__":
    # start_playing('/Users/harsh/Documents/Rezo/Clients/MarutiV2/Sales Release/All_Cases/language_cases.csv','silencefound',15)
    #start_playing('D:/voice_dumps/nexa_voice.csv', 'मेरी', 7)
    #start_playing('D:/voice_dumps/hyperlocal_map.csv','bing .',6)
    start_playing('C://Users//HR OFFICE//Downloads//new_psf_2.csv', 'सोलन।',3,0)
    # print(pd.read_csv('C://Users//HR OFFICE//Downloads//psf_call.csv',encoding='utf-8'))
