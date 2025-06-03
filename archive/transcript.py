from moviepy import VideoFileClip, TextClip, CompositeVideoClip, AudioFileClip
from openai import OpenAI

from config import OPENAI_API_KEY

from pprint import pprint
import os
import traceback

client = OpenAI(api_key=OPENAI_API_KEY)

def get_transcript(self):
        transcription = client.audio.transcriptions.create(
            file=self._get_audio_file(),
            model="whisper-1",
            response_format="verbose_json",
            timestamp_granularities=["word"]
        )
        return transcription

def get_text(self, transcript):
    text = []
    for word in transcript.words:
        text.append(word.word)
    return " ".join(text)


if __name__ == "__main__":
    transcript = get_transcript("clips/kci.mp4")
    text = get_text(transcript)
    print(text)