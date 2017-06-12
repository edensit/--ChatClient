import pyaudio
import os
import thread

CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
RATE = 44100


def play_sound(path):
    thread.start_new_thread(perform_play_sound, (path,))


def perform_play_sound(path):
    file_size = os.path.getsize(path)
    p = pyaudio.PyAudio()
    output = p.open(format=FORMAT, channels=1, rate=RATE, output=True)

    with open(path, 'rb') as fh:
        while fh.tell() != file_size:
            audio_frame = fh.read(CHUNK_SIZE)
            output.write(audio_frame)
