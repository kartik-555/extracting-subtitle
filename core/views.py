import subprocess
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views import View
from django.views.generic import ListView, DetailView
from .models import Video, Subtitle
from .forms import VideoForm
import os

def home(request):
    return render(request, 'index.html')

class UploadVideoView(View):
    def get(self, request):
        form = VideoForm()
        return render(request, 'upload.html', {'form': form})

    def post(self, request):
        form = VideoForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save()
            self.process_video(video.id)
            return JsonResponse({'message': 'Video uploaded successfully'})
        return render(request, 'upload.html', {'form': form})

    def process_video(self, video_id):
        video = Video.objects.get(id=video_id)
        video_path = video.file.path
        subtitle_path = f"{video_path}.srt"

        # Run ccextractor to extract subtitles
        result = subprocess.run(['ccextractor', video_path, '-o', subtitle_path], capture_output=True, text=True)

        if result.returncode == 0:
            Subtitle.objects.create(video=video, language='en', content=subtitle_path)
        else:
            print(result.returncode, "Error extracting subtitles")

class ListVideosView(View):
    def get(self, request):
        videos = Video.objects.all()
        return render(request, 'list_videos.html', {'videos': videos})

class VideoDetailView(DetailView):
    model = Video
    template_name = 'video_detail.html'
    context_object_name = 'video'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subtitles = self.object.subtitles.all()
        context['subtitles'] = [{'language': subtitle.language, 'content': subtitle.content} for subtitle in subtitles]
        return context

class SearchSubtitlesView(View):
    def get(self, request, video_id):
        query = request.GET.get('q', '')
        video = get_object_or_404(Video, id=video_id)
        subtitles = video.subtitles.filter(content__icontains=query)
        return JsonResponse({'results': [{'timestamp': s.timestamp, 'text': s.text} for s in subtitles]})