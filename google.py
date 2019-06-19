import datetime
import shutil
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.video.io.VideoFileClip import VideoFileClip
import requests
from moviepy.editor import *
import os
import speech_recognition as sr
from pydub import AudioSegment
import boto3

s3 = boto3.resource('s3')


def getTimeCode(seconds):
    # Format and return a string that contains the converted number of seconds into SRT format

    thund = int(seconds % 1 * 1000)
    tseconds = int(seconds)
    tsecs = ((float(tseconds) / 60) % 1) * 60
    tmins = int(tseconds / 60)
    return str("%02d:%02d:%02d.%03d" % (00, tmins, int(tsecs), thund))


def getaudio(video, audioname):
    videopath = "./media/" + video
    video = VideoFileClip(videopath)

    audio = video.audio
    audiopath = "./media/" + audioname
    audio.write_audiofile(audiopath)
    s3.Object('speechtotextextractor', os.path.basename(audiopath)).upload_file(Filename=audiopath)
    audioslicing(audiopath)
    os.remove(audiopath)
    # embedsubtitle(videopath)
    # os.remove(videopath)
    return "/media/"+os.path.basename(videopath)


def audioslicing(audiopath):
    try:
        os.mkdir('./media/chunks/')
    except:
        pass
    audio = AudioSegment.from_wav(audiopath)
    n = len(audio)
    counter = 1
    interval = 5 * 1000
    overlap = 1.5 * 1000
    start = 0
    end = 0
    flag = 0
    f = open("./media/subtitle.srt", "w+")

    for i in range(0, n, interval):
        if i == 0:
            start = 0
            end = interval
        else:
            start = end - overlap
            end = start + interval
        if end >= n:
            end = n
            flag = 1
        chunk = audio[start:end]
        filename = './media/chunks/chunk' + str(counter) + ".wav"
        chunk.export(filename, format="wav")
        googleService(filename, f)
        os.remove(filename)
        counter += 1
    f.close()


def googleService(filename, f):
    r = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio_listened = r.listen(source)
    try:
        rec = r.recognize_google(audio_listened)
        print(rec)
        f.write(rec + " ")
    except:
        pass


def embedsubtitle(videopath):
    try:
        os.mkdir("./media/output")
    except:
        pass
    generator = lambda txt: TextClip(txt, font='Georgia-Regular', fontsize=40, color='white')
    sub = SubtitlesClip("./media/subtitle.srt", generator)
    myvideo = VideoFileClip(videopath)
    final = CompositeVideoClip([myvideo, sub.set_position(('center', 'bottom'))])
    final.write_videofile('./media/output/' + os.path.basename(videopath), fps=myvideo.fps)
