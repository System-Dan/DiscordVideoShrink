# DiscordVideoShrink
This script compresses video files to fit within Discord's 25 MB file sharing limit.

Requires static build of ffmpeg and ffprobe, use ffmpeg-master-latest-win64-gpl.zip from here https://github.com/BtbN/FFmpeg-Builds/releases. 
ffmpeg and ffprobe can be either be added to PATH or same directory as the script. 

The script will try to encode 2 pass with libx264, failing that it will revert to libx265 and if that's not available it will use ffmpeg's mpeg4. 

1. Run with python DiscordVideoShrink.py
2. Enter file path and filename of video
3. File will be re-encoded and renamed to reencoded-videoname.mp4
