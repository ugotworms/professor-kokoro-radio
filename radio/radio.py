import asyncio
import threading
import json
import numpy as np
from datetime import datetime
from pydub import AudioSegment
from pydub.playback import play
import inflect

from .config import Config
from .story import Story
from .weather import Weather
from .audio import Audio

class Radio:
    def __init__(self, kokoro):
        self.kokoro = kokoro
        self.config = Config()
        self.story = Story()
        self.weather = Weather()
        self.audio = Audio()
        self.queue = asyncio.Queue()

    def get_time(self):
        p = inflect.engine()
        now = datetime.now()
        hour = now.strftime("%I")
        minute = now.strftime("%M")
        period = now.strftime("%p").lower()

        if minute == "00":
            time_text = f"{p.number_to_words(hour)} o'clock {period.upper()}"
        else:
            time_text = f"{p.number_to_words(hour)} {p.number_to_words(minute, group=2, zero='oh')} {period.upper()}"

        if 5 <= now.hour < 12:
            time_of_day = "morning"
        elif 12 <= now.hour < 18:
            time_of_day = "afternoon"
        else:
            time_of_day = "evening"

        return (time_of_day, time_text)

    async def time_weather_producer(self, station):
        with open('headlines.json', 'r') as file:
            headlines = json.load(file)

        while True:
            if datetime.now().minute == 0:
                bell = AudioSegment.from_file("audio/single-church-bell-156463.mp3")
                hour = datetime.now().hour
                if hour > 12:
                    hour = hour - 12
                for i in range(hour):
                    await asyncio.sleep(1.7)
                    threading.Thread(target=play, args=(bell,)).start()

            time_of_day, time_text = self.get_time()
            await self.queue.put(f"Good {time_of_day}, the time is now {time_text}.")
            weather_text = await self.weather.get_weather(station)
            await self.queue.put(weather_text)

            if np.random.randint(1, 6) == 5:
                headline = headlines[np.random.randint(0, len(headlines))]
                print(f"[headline]: {headline['headline']}")
                await asyncio.sleep(20)
                await self.queue.put(f"Thank you for tuning in, my name is Professor Kokoro. Today is {headline['date']}. {headline['headline']} The time is now {time_text}")
                await asyncio.sleep(60)
            else:
                await asyncio.sleep(60)

    async def story_producer(self):
        config = self.config.load_config()
        corpus_lines = self.story.load_corpus_lines(config["story"])
        char_counter = 0
        while True:
            if self.queue.qsize() > 2:
                await asyncio.sleep(0.5)
                continue
            config = self.config.load_config()
            if config["line"] < len(corpus_lines):
                line = corpus_lines[config["line"]]
                await self.queue.put(line)
                config["line"] += 1
                self.config.save_config(config)
                char_counter += len(line)
                if char_counter > 1000:
                    await asyncio.sleep(2.0)
                    await self.queue.put("::PAGETURN::")
                    char_counter = 0
            else:
                await asyncio.sleep(2.0)
                await self.queue.put(f"Thank you for listening to {config['title']} by {config['author']}. We will now begin a new story.")
                await asyncio.sleep(2.0)
                new_story_file = self.story.choose_random_story(config["story"])
                config = self.story.init_new_story(new_story_file, config)
                self.config.save_config(config)
                corpus_lines = self.story.load_corpus_lines(new_story_file)
                opening_line = f"We now begin the tale '{config['title']}' by {config['author']}."
                await asyncio.sleep(2.0)
                await self.queue.put(opening_line)

            await asyncio.sleep(0.1)

    def start_input_thread(self):
        def start_repl(loop, queue):
            asyncio.set_event_loop(loop)
            while True:
                user_input = input("Say:")
                asyncio.run_coroutine_threadsafe(queue.put(user_input), loop)

        loop = asyncio.get_event_loop()
        repl_thread = threading.Thread(target=start_repl, args=(loop, self.queue))
        repl_thread.daemon = True
        repl_thread.start()

    async def run(self, mode="time_weather"):
        if mode == "story":
            config = self.config.load_config()
            if config["story"] == "":
                story_file = self.story.choose_random_story("")
                config = self.story.init_new_story(story_file, config)
                self.config.save_config(config)

            if config["line"] > 1:
                opening_line = f"We now continue the story {config['title']}, by {config['author']}."
            else:
                opening_line = f"We now begin the tale '{config['title']}' by {config['author']}."

            await self.queue.put(opening_line)
            await self.queue.put("::PAGETURN::")
            producer_task = asyncio.create_task(self.story_producer())
        else:
            producer_task = asyncio.create_task(self.time_weather_producer("FOXR1"))

        consumer_task = asyncio.create_task(self.audio.buffered_audio_consumer(self.queue, self.kokoro))
        music_task = asyncio.create_task(self.audio.background_music_player("audio/radio_background.mp3"))

        self.start_input_thread()

        await asyncio.gather(producer_task, consumer_task, music_task)
