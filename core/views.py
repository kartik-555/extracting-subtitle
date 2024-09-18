import subprocess
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views import View
from django.views.generic import DetailView
from django.conf import settings
from .models import Video, Subtitle
from .forms import VideoForm
import webvtt
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

    def convert_srt_to_vtt(self, subtitle_path, vtt_path):
        with open(subtitle_path, 'r', encoding='utf-8') as srt_file:
            srt_content = srt_file.readlines()

        vtt_content = ['WEBVTT\n\n']  # Start with the WEBVTT header

        for line in srt_content:
            # Replace commas in timestamps with dots
            if '-->' in line:
                line = line.replace(',', '.')

            vtt_content.append(line)

        # Write the new VTT content to a file
        with open(vtt_path, 'w', encoding='utf-8') as vtt_file:
            vtt_file.writelines(vtt_content)

        print(f"Conversion complete: {vtt_path}")

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
            self.convert_srt_to_vtt(subtitle_path, vtt_path)

            relative_vtt_path = os.path.relpath(vtt_path, settings.MEDIA_ROOT)
            full_vtt_path = f"{settings.MEDIA_URL}{relative_vtt_path}"
            subtitle = Subtitle(video=video, language='en', content=full_vtt_path)
            subtitle.save()
            os.remove(subtitle_path)
        else:
            print(result.returncode, "Error extracting subtitles")

class ListVideosView(View):
    def get(self, request):
        videos = Video.objects.all().order_by('-uploaded_at')
        return render(request, 'list_videos.html', {'videos': videos})


class VideoDetailView(DetailView):
    model = Video
    template_name = 'video_detail.html'
    context_object_name = 'video'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '')
        subtitles = self.object.subtitles.all()
        search_results = []

        if query:
            for subtitle in subtitles:
                vtt_path = subtitle.content
                vtt_file_path = os.path.join(settings.MEDIA_ROOT, vtt_path.replace(settings.MEDIA_URL, ''))
                if os.path.exists(vtt_file_path):
                    results = self.search_vtt_for_query(vtt_file_path, query)
                    search_results.extend(results)

        context['search_results'] = search_results
        context['subtitles'] = [{'language': subtitle.language, 'content': subtitle.content} for subtitle in subtitles]
        context['query'] = query
        return context

    def search_vtt_for_query(self, vtt_file_path, query):
        results = []
        for caption in webvtt.read(vtt_file_path):
            if query.lower() in caption.text.lower():
                results.append({'timestamp': caption.start, 'text': caption.text})
        return results

class SearchSubtitlesView(View):
    def get(self, request, video_id):
        query = request.GET.get('q', '')
        video = get_object_or_404(Video, id=video_id)
        subtitles = video.subtitles.filter(content__icontains=query)
        return JsonResponse({'results': [{'timestamp': s.timestamp, 'text': s.text} for s in subtitles]})