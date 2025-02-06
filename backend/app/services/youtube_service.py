import asyncio
import glob
import json
import os
import re
import subprocess
from typing import Dict

import yt_dlp

from .aws_service import AwsService
from ..core.exceptions import YouTubeDownloadError
aws_service = AwsService()

class YouTubeService:
    def __init__(self):
        self._check_yt_dlp()

    def _check_yt_dlp(self):
        try:
            subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise YouTubeDownloadError("yt-dlp is not installed")

    def validate_url(self, url: str) -> bool:
        """Validate if the URL is a valid YouTube URL"""
        # Basic URL validation using regex
        youtube_regex = (
            r'(https?://)?(www\.)?'
            '(youtube|youtu|youtube-nocookie)\.(com|be)/'
            '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
        )

        if not re.match(youtube_regex, url):
            print("Error: Invalid YouTube URL format")
            return False

        try:
            cmd = ["yt-dlp", "--simulate", "--no-warnings", url]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return True
        except subprocess.CalledProcessError as e:
            error_message = e.stderr.lower()
            if "unable to download webpage" in error_message:
                print("Error: Unable to access the video. It may be private or restricted.")
            elif "video unavailable" in error_message:
                print("Error: The video is unavailable or does not exist.")
            else:
                print(f"Error: {e.stderr.strip()}")
            return False

    def get_youtube_video_title(self, url: str) -> str:
        # Configure yt-dlp to only extract information without downloading the video.
        ydl_opts = {
            'quiet': True,
            # 'skip_download': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract video information as a dictionary
            info_dict = ydl.extract_info(url)
            # The video title is available in the 'title' key.
            js = json.dumps(ydl.sanitize_info(info_dict)['fulltitle']).split('"')[1]
            # return info_dict.get('title', 'Unknown Title')
            return js

    async def get_formats(self, url: str) -> Dict:
        try:
            cmd = ["yt-dlp", "-F", url]
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()

            if proc.returncode != 0:
                raise YouTubeDownloadError(f"Failed to get formats: {stderr.decode()}")

            output = stdout.decode()
            return self._parse_formats(output)

        except Exception as e:
            raise YouTubeDownloadError(f"Error getting formats: {str(e)}")

    def _parse_formats(self, output: str) -> Dict:
        available_qualities = {}
        available_video_formats = set()
        available_audio_formats = set()

        video_lines = [line for line in output.split('\n') if 'video only' in line.lower()]
        max_height = 0

        for line in video_lines:
            match = re.search(r'(\d+)p', line)
            if match:
                height = int(match.group(1))
                max_height = max(max_height, height)

            for format_type in ['mp4', 'webm', 'mkv']:
                if format_type in line.lower():
                    available_video_formats.add(format_type)

        quality_map = {
            '4320p': 4320, '2160p': 2160, '1440p': 1440,
            '1080p': 1080, '720p': 720, '480p': 480,
            '360p': 360, '240p': 240, '144p': 144
        }

        for quality, height in quality_map.items():
            if height <= max_height:
                available_qualities[quality] = f'bestvideo[height<={height}]+bestaudio/best[height<={height}]'

        available_qualities['best'] = 'bestvideo+bestaudio/best'

        audio_lines = [line for line in output.split('\n') if 'audio only' in line.lower()]
        for line in audio_lines:
            for format_type in ['mp3', 'm4a', 'aac', 'opus', 'flac', 'wav']:
                if format_type in line.lower():
                    available_audio_formats.add(format_type)

        return {
            "available_qualities": available_qualities,
            "video_formats": list(available_video_formats),
            "audio_formats": list(available_audio_formats)
        }

    async def download_video(self, url: str, quality: str, output_format: str) -> Dict:
        try:
            # First get available formats
            formats = await self.get_formats(url)

            # Get the format string for requested quality
            format_quality_string = formats['available_qualities'].get(quality)
            if not format_quality_string:
                available_qualities = list(formats['available_qualities'].keys())
                raise YouTubeDownloadError(
                    f"Requested quality '{quality}' is not available. "
                    f"Available qualities are: {', '.join(available_qualities)}"
                )

            if output_format not in formats['video_formats']:
                available_formats = formats['video_formats']
                raise YouTubeDownloadError(
                    f"Requested format '{output_format}' is not available. "
                    f"Available formats are: {', '.join(available_formats)}"
                )

            # output_template = "downloads/%(title)s-%(resolution)s.%(ext)s"
            output_template = f"downloads/{self.get_youtube_video_title(url)}-{quality}.{output_format}"
            os.makedirs("downloads", exist_ok=True)

            # Modified format string to ensure we get both video and audio
            if quality == 'best':
                format_quality_string = 'bestvideo+bestaudio/best'
            else:
                # Extract height from quality (e.g., '720p' -> '720')
                height = quality.replace('p', '')
                format_quality_string = f'bestvideo[height<={height}]+bestaudio/best[height<={height}]'

            cmd = [
                "yt-dlp",
                "-f", format_quality_string,
                "--merge-output-format", output_format,  # Force merge to specified format
                "-o", output_template,
                "--no-playlist",
                "--no-write-thumbnail",
                "--no-embed-thumbnail",
                "--no-write-description",
                "--no-write-info-json",
                "--progress",
                "--prefer-ffmpeg",
                url
            ]

            print(f"\nStarting download in {quality} ({output_format} format)...")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )

            if result.returncode != 0:
                raise YouTubeDownloadError(f"Download failed: {result.stdout}")

            # Post-download renaming: yt-dlp appends extra text to the filename, so we need to rename the file to remove it.
            expected_filename = f"{self.get_youtube_video_title(url)}-{quality}.{output_format}"
            expected_filepath = os.path.join("downloads", expected_filename)

            # Create a glob pattern that matches files starting with the expected name but possibly with extra text before the extension.
            # For example, if yt-dlp appends '.f248' then the file might be:
            # "downloads/Recursion tree method ...-1080p.f248.webm"
            pattern = os.path.join("downloads", f"{self.get_youtube_video_title(url)}-{quality}*{'.' + output_format}")
            matching_files = glob.glob(pattern)

            # Look for a file that doesn't exactly match our expected name.
            for file_path in matching_files:
                if os.path.basename(file_path) != expected_filename:
                    print(f"Renaming {file_path} to {expected_filepath}")
                    os.rename(file_path, expected_filepath)
                    break  # Assuming only one such file exists

            # Upload the downloaded video to S3
            download_url = aws_service.upload_file(expected_filepath)
            if not download_url:
                raise YouTubeDownloadError("Failed to upload the downloaded video to S3")

            if os.path.exists(expected_filepath):
                os.remove(expected_filepath)
            else:
                print(f"The file {expected_filepath} does not exist")

            return {
                "status": "success",
                "message": f"Video downloaded successfully. Go to this link to download the media - {download_url}",
            }

        except YouTubeDownloadError:
            raise
        except Exception as e:
            raise YouTubeDownloadError(f"Error downloading video: {str(e)}")

    async def download_audio(self, url: str, audio_format: str, audio_quality: str = "0") -> Dict:
        if not audio_quality.isdigit() or int(audio_quality) not in range(10):
            raise YouTubeDownloadError("Audio quality must be between 0 (best) and 9 (worst)")

        # output_template = "downloads/%(title)s-%(abr)s.%(ext)s"
        output_template = f"downloads/{self.get_youtube_video_title(url)}.{audio_format}"

        try:
            cmd = [
                "yt-dlp",
                "-f", "bestaudio",
                "--extract-audio",
                "--audio-format", audio_format,
                "--audio-quality", audio_quality,
                "-o", output_template,
                "--no-playlist",
                url
            ]

            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()

            if proc.returncode != 0:
                raise YouTubeDownloadError(f"Download failed: {stderr.decode()}")

            # Post-download renaming: yt-dlp appends extra text to the filename, so we need to rename the file to remove it.
            expected_filename = f"{self.get_youtube_video_title(url)}.{audio_format}"
            expected_filepath = os.path.join("downloads", expected_filename)

            # Create a glob pattern that matches files starting with the expected name but possibly with extra text before the extension.
            # For example, if yt-dlp appends '.f248' then the file might be:
            # "downloads/Recursion tree method ...-1080p.f248.webm"
            pattern = os.path.join("downloads",
                                   f"{self.get_youtube_video_title(url)}*{'.' + audio_format}")
            matching_files = glob.glob(pattern)

            # Look for a file that doesn't exactly match our expected name.
            for file_path in matching_files:
                if os.path.basename(file_path) != expected_filename:
                    print(f"Renaming {file_path} to {expected_filepath}")
                    os.rename(file_path, expected_filepath)
                    break  # Assuming only one such file exists

            # Upload the downloaded video to S3
            download_url = aws_service.upload_file(expected_filepath)
            if not download_url:
                raise YouTubeDownloadError("Failed to upload the downloaded video to S3")

            if os.path.exists(expected_filepath):
                os.remove(expected_filepath)
            else:
                print(f"The file {expected_filepath} does not exist")

            return {
                "status": "success",
                "message": f"Audio downloaded successfully. Go to this link to download the media - {download_url}",
            }
        except Exception as e:
            raise YouTubeDownloadError(f"Error downloading audio: {str(e)}")
