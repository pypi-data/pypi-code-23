import simpleaudio as sa

wave_obj = sa.WaveObject.from_wave_file("sounds/laser1.wav")
print(type(wave_obj))
play_obj = wave_obj.play()
play_obj.wait_done()