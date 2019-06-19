import os
import boto3
import requests
from moviepy.editor import *

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
    aws(os.path.basename(audiopath), os.path.basename(videopath))
    os.remove(audiopath)
    return os.path.basename(videopath)


def aws(medialurl, videoname):
    client = boto3.client(
        'transcribe',
        # aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
        # aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
        region_name='us-east-1'
    )
    try:
        client.delete_transcription_job(TranscriptionJobName=videoname)
    except:
        pass
    response = client.start_transcription_job(
        TranscriptionJobName=videoname,
        LanguageCode='en-US',
        MediaFormat='mp3',
        OutputBucketName='speechtotextextractor',
        Media={'MediaFileUri': 'https://speechtotextextractor.s3.amazonaws.com/' + medialurl}

    )

    f = open("./media/" + videoname + ".vtt", "w+")
    srt = open("./media/" + videoname + ".srt", "w+")
    f.write("WEBVTT\n\n")
    while True:
        status = client.get_transcription_job(TranscriptionJobName=videoname)
        if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            break
        print("Not ready yet...")
        os.system("clear")
    url = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
    r = requests.get(url)
    speechtext = r.json()
    words = speechtext['results']["items"]
    sortedwords = []  # remove punctuations
    for word in words:
        if word['type'] == 'pronunciation':
            sortedwords.append(word)

    words = sortedwords

    counter = 1
    limit = 10
    phrase = limit
    sublist = []
    for index, word in enumerate(words, start=1):
        if index == phrase:
            sublist[counter - 1]['end'] = word['end_time']

            sublist[counter - 1]['text'] = sublist[counter - 1]['text'] + word['alternatives'][0]['content'] + " "
            counter += 1
            phrase = limit * counter
        else:
            if phrase - index == 9:
                sublist.append({
                    "start": word['start_time'],
                    "end": "",
                    "text": ""})

            sublist[counter - 1]['text'] = sublist[counter - 1]['text'] + word['alternatives'][0]['content'] + " "
            if len(words) - 1 == index:
                sublist[counter - 1]['end'] = word['end_time']

    for index, word in enumerate(sublist, start=1):
        srt.write(str(index) + "\n")
        srt.write(
            getTimeCode(float(word['start'])).replace('.', ',') + " --> " + getTimeCode(float(word['end'])).replace('.',
                                                                                                                    ',') + "\n")
        f.write(getTimeCode(float(word['start'])) + " --> " + getTimeCode(float(word['end'])) + "\n")
        if index < len(sublist):
            f.write(word['text'] + '\n\n')
        else:
            f.write(word['text'])
        srt.write(word['text'] + '\n\n')

    f.close()
    srt.close()
    client.delete_transcription_job(TranscriptionJobName=videoname)
    s3.Object('speechtotextextractor', medialurl).delete()
