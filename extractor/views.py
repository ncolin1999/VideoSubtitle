import os

from celery import shared_task
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from extractor.speech.audioextractor import getaudio

loading = ''


# Create your views here.
class FileUpload(View):

    def get(self, request):
        return render(request, "home.html")

    def post(self, request):
        p = request.FILES['file']
        fs = FileSystemStorage()
        file = fs.save(p.name, p)
        video = start_recognition(file)
        # video = getaudio(file, file[:-4] + ".mp3")
        '''chunk_size = 65536
        rem = p.size % chunk_size
        num_chunks = p.size / chunk_size
        if rem == 0:
            pass
        else:
            num_chunks += 1
        i = 0
        check.delay()
        with open(f'./video/{p.name}', 'wb+') as data:
            for chunk in p.chunks():
                data.write(chunk)
                i += 1
                os.system('clear')
                global loading
                loading = str(round((i * 100) / num_chunks)) + "%"
                print(loading)
            print()'''
        data = {"video": "/media/" + video,
                "subtitle": "/media/" + video + ".vtt",
                "download": "/media/" + video + ".srt"
                }
        return JsonResponse(data)


@shared_task
def start_recognition(file):
    video = getaudio(file, file[:-4] + ".mp3")
    return video
