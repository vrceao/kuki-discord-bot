import sys
import os
import wave

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import aquestalk

aq = aquestalk.load('f1')
wav = aq.synthe("こんにちわ")

params = wav.getparams()
frames = wav.readframes(wav.getnframes())

with wave.open("output.wav", "wb") as output_file:
    output_file.setparams(params)
    output_file.writeframes(frames)