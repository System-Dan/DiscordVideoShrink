import subprocess
import os

def check_encoder(encoder_name):
    """
    Checks if the specified encoder is available in ffmpeg.
    """
    result = subprocess.run(['ffmpeg', '-codecs'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return encoder_name in result.stdout.decode()

def get_video_length(filename):
    """
    Gets the length of the video in seconds using ffprobe.
    """
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', filename],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    return float(result.stdout)

def calculate_video_bitrate(video_length, target_size_mb, audio_bitrate_kbps):
    """
    Calculates the required video bitrate to achieve the target file size.
    """
    target_size_bits = target_size_mb * 8 * 1024 * 1024  # Convert MB to bits
    audio_bitrate_bps = audio_bitrate_kbps * 1000  # Convert kbps to bps

    # Total audio bitrate for both streams
    total_audio_bitrate_bps = 2 * audio_bitrate_bps

    # Calculate the video bitrate
    video_bitrate_bps = (target_size_bits / video_length) - total_audio_bitrate_bps
    return video_bitrate_bps / 1000  # Convert bps to kbps

def reencode_video_two_pass(input_filename, output_filename, video_bitrate_kbps, video_encoder):
    """
    Re-encodes the video stream with the specified bitrate using two-pass encoding
    while copying the audio streams.
    """
    # First pass
    subprocess.run([
        'ffmpeg', '-y', '-i', input_filename, '-c:v', video_encoder, '-b:v', f'{video_bitrate_kbps}k',
        '-pass', '1', '-an', '-f', 'null', '/dev/null' if os.name != 'nt' else 'NUL'
    ])

    # Second pass
    subprocess.run([
        'ffmpeg', '-i', input_filename, '-c:v', video_encoder, '-b:v', f'{video_bitrate_kbps}k',
        '-pass', '2', '-c:a', 'copy', '-map', '0', output_filename
    ])

def main():
    input_filename = input("Enter the path to the MP4 file: ").strip()
    
    if not os.path.isfile(input_filename):
        print("File does not exist.")
        return

    # Check for available video encoder
    video_encoder = 'libx264'
    if not check_encoder(video_encoder):
        print(f"Encoder {video_encoder} not found. Trying libx265.")
        video_encoder = 'libx265'
        if not check_encoder(video_encoder):
            print(f"Encoder {video_encoder} not found. Using mpeg4.")
            video_encoder = 'mpeg4'

    output_filename = "reencoded_" + os.path.basename(input_filename)
    
    # Get the length of the video in seconds
    video_length = get_video_length(input_filename)
    print(f"Video length: {video_length} seconds")

    # Calculate the required video bitrate
    target_size_mb = 24.5
    audio_bitrate_kbps = 192
    video_bitrate_kbps = calculate_video_bitrate(video_length, target_size_mb, audio_bitrate_kbps)
    print(f"Calculated video bitrate: {video_bitrate_kbps} kbps")

    # Re-encode the video using two-pass encoding
    reencode_video_two_pass(input_filename, output_filename, video_bitrate_kbps, video_encoder)
    print(f"Re-encoded video saved as: {output_filename}")

if __name__ == "__main__":
    main()
