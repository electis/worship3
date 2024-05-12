import glob
import os
import random

from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.VideoClip import TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.io.VideoFileClip import VideoFileClip

from bible import bible
from conf import read_config


def main():
    conf = read_config()

    audio_files = glob.glob(conf.audio_path)
    random.shuffle(audio_files)

    for f in glob.glob(os.path.join(conf.tmp_path, '*')):
        os.remove(f)

    random.shuffle(bible)

    background_video = VideoFileClip(conf.video_file)

    audio_clips = [AudioFileClip(file) for file in audio_files]

    playing_time = 0
    audio_with_text = []
    for i, clip in enumerate(audio_clips):
        text_clip = TextClip(bible[i], fontsize=50, color='white').set_position((10, 10))
        audio_with_text.append(CompositeAudioClip([audio_clips[i], text_clip]))

        playing_time += audio_clips[i].duration
        if playing_time > conf.stop_after:
            break

    final_clip = CompositeVideoClip([background_video] + audio_with_text)

    # TODO stream, create tmp dir
    final_clip.write_videofile(conf.tmp_path + '/output.mp4', fps=24, codec='libx264', bitrate='5M')


if __name__ == '__main__':
    main()
