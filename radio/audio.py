import asyncio
import threading
import random
import numpy as np
from pydub import AudioSegment
from pydub.playback import play
from queue import Queue as ThreadingQueue

class Audio:
    def play_forever(self, audio):
        while True:
            play(audio)

    async def background_music_player(self, audio_path):
        track = AudioSegment.from_file(audio_path)
        music_thread = threading.Thread(target=self.play_forever, args=(track,))
        music_thread.daemon = True
        music_thread.start()

    async def buffered_audio_consumer(self, queue, kokoro):
        buffer_queue = ThreadingQueue()

        def play_buffered_audio():
            while True:
                audio_segment = buffer_queue.get()
                play(audio_segment)
                buffer_queue.task_done()

        play_thread = threading.Thread(target=play_buffered_audio)
        play_thread.daemon = True
        play_thread.start()

        while True:
            if not queue.empty():
                if buffer_queue.qsize() > 2:
                    await asyncio.sleep(0.5)
                    continue
                text = await queue.get()
                if text == "::PAGETURN::":
                    buffer_queue.put(AudioSegment.from_file(f"audio/pageturn0{random.randint(1, 4)}.wav"))
                    continue
                print(text)
                speed = random.uniform(0.8, 1.0)
                bm_lewis: np.ndarray = kokoro.get_voice_style("bm_lewis")
                stream = kokoro.create_stream(text, voice=bm_lewis, speed=speed, lang="en-us")
                async for samples, sample_rate in stream:
                    int16_data = (samples * 32767).astype(np.int16)
                    audio = AudioSegment(
                        int16_data.tobytes(),
                        frame_rate=sample_rate,
                        sample_width=2,
                        channels=1
                    )
                    stereo_audio = AudioSegment.from_mono_audiosegments(AudioSegment.silent(duration=10) + audio, audio + AudioSegment.silent(duration=10))
                    stereo_audio = stereo_audio + AudioSegment.silent(duration=1000)
                    stereo_audio = stereo_audio - 5
                    buffer_queue.put(stereo_audio)

            await asyncio.sleep(0.1)
