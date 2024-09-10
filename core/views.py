import subprocess
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views import View
from django.views.generic import ListView, DetailView
from .models import Video, Subtitle
from .forms import VideoForm
import srt
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

        # Split the video path into name and extension
        base_path, _ = os.path.splitext(video_path)
        subtitle_path = f"{base_path}.srt"
        vtt_path = f"{base_path}.vtt"

        # Run ccextractor to extract subtitles
        result = subprocess.run(['ccextractor', video_path, '-o', subtitle_path], capture_output=True, text=True)

        if result.returncode == 0:
            # Convert .srt to .vtt
            with open(subtitle_path, 'r') as srt_file:
                srt_content = srt_file.read()
                subtitles = list(srt.parse(srt_content))
                vtt_content = "WEBVTT\n\n" + srt.compose(subtitles)

            with open(vtt_path, 'w') as vtt_file:
                vtt_file.write(vtt_content)

            # Save the subtitle information
            Subtitle.objects.create(video=video, language='en', content=vtt_path)
            os.remove(subtitle_path)
        else:
            print(result.returncode, "Error extracting subtitles")

class ListVideosView(View):
    def get(self, request):
        query = request.GET.get('q', '')
        if query:
            videos = Video.objects.filter(subtitles__content__icontains=query).distinct()
        else:
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