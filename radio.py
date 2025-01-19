import asyncio
import threading
import os
import random
import json
import requests
import sounddevice as sd
import numpy as np
from pydub import AudioSegment
from pydub.playback import play
from kokoro_onnx import Kokoro
from datetime import datetime
from queue import Queue as ThreadingQueue
import inflect


# Function to play an audio segment in an infinite loop
def play_forever(audio):
    while True:
        play(audio)

# Load configuration from a JSON file
def load_config():
    with open("radio_config.json", "r") as f:
        return json.load(f)

# Save configuration to a JSON file
def save_config(config):
    with open("radio_config.json", "w") as f:
        json.dump(config, f)

# Choose a random story file from the corpus directory, ignoring a specified file
def choose_random_story(ignore):    
    corpus_dir = "corpus"
    corpus_files = [f for f in os.listdir(corpus_dir) if f != ignore and os.path.isfile(os.path.join(corpus_dir, f))]
    random_story = random.choice(corpus_files)
    return random_story

# Initialize a new story by loading its first line and updating the config
def init_new_story(story_file):
    with open(f"corpus/{story_file}", "r") as f:
        lines = f.readlines()
    config = load_config()
    config["title"] = lines[0].strip()
    config["line"] = 1
    config["story"] = f"{story_file}"
    save_config(config)
    return config

# Load lines from a story file and correct pronunciation of specific words
def load_corpus_lines(story_file):
    with open(f"corpus/{story_file}", "r") as f:
        lines = f.readlines()
    # Remove blank/empty lines and convert unique Lovecraftian words to phonetic spelling
    lines = [correct_pronuncation(line) for line in lines if line.strip()]
    return lines[1:]

# Correct pronunciation of specific Lovecraftian words
def correct_pronuncation(text):
    text = text.replace("Miskatonic", "miss-kuh-tonic")
    text = text.replace("Arkham", "ark-hum")
    text = text.replace("Cthulhu", "kuh-thewloo")
    #text = text.replace("Necronomicon", "neck-row-nom-ih-con")
    text = text.replace("R'lyeh", "rill-ee-uh")
    text = text.replace("Nyarlathotep", "nye-are-lath-oh-tep")    
    text = text.replace("Yog-Sothoth", "yog-so-thoth")
    text = text.replace("Pnakotic", "nuh-kah-tick")
    return text

# Play background music tracks in an infinite loop
async def background_music_player(audio_path):
    track = AudioSegment.from_file(audio_path)
    music_thread = threading.Thread(target=play_forever, args=(track,));
    music_thread.daemon = True
    music_thread.start()

# Fetch weather data from a weather station and format it into a string
async def get_weather(station):
    getUrl = f'https://api.weather.gov/stations/{station}/observations/latest'
    try:
        response = requests.get(getUrl)
        response.raise_for_status()
        weather_data = response.json()
        temperature = weather_data['properties']['temperature']['value']
        # Convert temperature to Fahrenheit and round to the nearest whole number
        temperature = int((temperature * 9/5) + 32)
        wind_speed = weather_data['properties']['windSpeed']['value']        
        wind_speed = int(wind_speed)
        wind_direction = weather_data['properties']['windDirection']['value']
        # Convert wind direction angle to a cardinal direction
        if 348.75 <= wind_direction < 11.25:
            wind_direction = "north"
        elif 11.25 <= wind_direction < 33.75:
            wind_direction = "north-northeast"
        elif 33.75 <= wind_direction < 56.25:
            wind_direction = "northeast"
        elif 56.25 <= wind_direction < 78.75:
            wind_direction = "east-northeast"
        elif 78.75 <= wind_direction < 101.25:
            wind_direction = "east"
        elif 101.25 <= wind_direction < 123.75:
            wind_direction = "east-southeast"
        elif 123.75 <= wind_direction < 146.25:
            wind_direction = "southeast"
        elif 146.25 <= wind_direction < 168.75:
            wind_direction = "south-southeast"
        elif 168.75 <= wind_direction < 191.25:
            wind_direction = "south"
        elif 191.25 <= wind_direction < 213.75:
            wind_direction = "south-southwest"
        elif 213.75 <= wind_direction < 236.25:
            wind_direction = "southwest"
        elif 236.25 <= wind_direction < 258.75:
            wind_direction = "west-southwest"
        elif 258.75 <= wind_direction < 281.25:
            wind_direction = "west"
        elif 281.25 <= wind_direction < 303.75:
            wind_direction = "west-northwest"
        elif 303.75 <= wind_direction < 326.25:
            wind_direction = "northwest"
        elif 326.25 <= wind_direction < 348.75:
            wind_direction = "north-northwest"
        else:
            wind_direction = "unknown"
            
        return f"The current temperature is a {describe_temperature(temperature)} {temperature} degrees Fahrenheit. The wind is at {wind_speed} miles per hour from the {wind_direction}."        
    except requests.exceptions.RequestException as e:
        print(f"Error getting weather data: {e}")
        return "I'm sorry, I was unable to retrieve the weather data at this time."

# Describe the temperature based on its value
def describe_temperature(temp_f):
    if temp_f < 20:
        return "Frigid"
    elif 20 <= temp_f < 40:
        return "Chilly"
    elif 40 <= temp_f < 60:
        return "Brisk"
    elif 60 <= temp_f < 80:
        return "Warm"
    elif 80 <= temp_f < 100:
        return "Hot"
    else:
        return "Scorching"   
    
# Get the current time and format it into a string
def get_time():
    p = inflect.engine()
    now = datetime.now()
    hour = now.strftime("%I")
    minute = now.strftime("%M")    
    period = now.strftime("%p").lower()
   
    if minute == "00":
        time_text = f"{p.number_to_words(hour)} o'clock {period.upper()}"
    else:
        time_text = f"{p.number_to_words(hour)} {p.number_to_words(minute,group=2,zero="oh")} {period.upper()}"

    if 5 <= now.hour < 12:
        time_of_day = "morning"
    elif 12 <= now.hour < 18:
        time_of_day = "afternoon"
    else:
        time_of_day = "evening"

    return f"Good {time_of_day}, the time is now {time_text}."

# Produce time and weather updates and add them to the queue
async def time_weather_producer(queue,station):
    while True:
        if(datetime.now().minute==0): #on the hour, play a bell sound for each hour
            bell = AudioSegment.from_file("audio/single-church-bell-156463.mp3")
            hour = datetime.now().hour
            if hour > 12:
                hour = hour - 12
            for i in range(hour):
                await asyncio.sleep(1.7) #allows for playing to overlap slightly
                threading.Thread(target=play, args=(bell,)).start()               
        
        time_text = get_time()
        await queue.put(time_text)   
        weather_text = await get_weather(station)        
        await queue.put(weather_text)
        await asyncio.sleep(60)  # Delay 60 seconds between updates

# Produce story lines and add them to the queue
async def story_producer(queue):
    config = load_config()
    corpus_lines = load_corpus_lines(config["story"])

    while True:
        # If the queue has 2+ items, wait until it's processed to avoid advancing the config line too quickly
        if queue.qsize() > 2:
            await asyncio.sleep(0.5)
            continue
        config = load_config()
        if config["line"] < len(corpus_lines):
            line = corpus_lines[config["line"]]
            await queue.put(line)
            config["line"] += 1
            save_config(config)
        else:         
            await asyncio.sleep(2.0)
            await queue.put(f"Thank you for listening to {config['title']} by {config['author']}. We will now begin a new story.")
            await asyncio.sleep(2.0)
            new_story = choose_random_story(config["story"])
            config = init_new_story(new_story)
            corpus_lines = load_corpus_lines(new_story)
            opening_line = f"We now begin the tale '{config['title']}' by {config['author']}."
            await asyncio.sleep(2.0)
            await queue.put(opening_line)   

        await asyncio.sleep(0.1)

# Start a thread to handle user input and add it to the queue
def start_input_thread(queue):
    def start_repl(loop, queue):
        asyncio.set_event_loop(loop)
        while True:
            user_input = input("Say:")
            asyncio.run_coroutine_threadsafe(queue.put(user_input), loop)
    
    loop = asyncio.get_event_loop()
    repl_thread = threading.Thread(target=start_repl, args=(loop, queue))
    repl_thread.daemon = True
    repl_thread.start()   

# Consume text from the queue, convert it to audio, and play it
async def buffered_audio_consumer(queue, kokoro):
    buffer_queue = ThreadingQueue()

    # Function to play buffered audio segments
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
            # If the buffer queue has more than 2 items, wait until it's processed to keep memory usage down
            if buffer_queue.qsize() > 2:
                await asyncio.sleep(0.5)
                continue
            text = await queue.get()
            print(text)
            #randomize speed between 0.8 and 1.0 for a more natural sound
            speed = random.uniform(0.8, 1.0)
            stream = kokoro.create_stream(text, voice="bm_lewis", speed=speed, lang="en-us")
            async for samples, sample_rate in stream:
                # Convert samples to AudioSegment
                audio = AudioSegment(
                    samples.tobytes(),
                    frame_rate=sample_rate,
                    sample_width=samples.dtype.itemsize,
                    channels=1
                )
                # Make the audio 2 channels with a slight delay to create a stereo effect
                stereo_audio = AudioSegment.from_mono_audiosegments(AudioSegment.silent(duration=10) + audio , audio + AudioSegment.silent(duration=10))
                # Add a 1-second silence at the end of the paragraph
                stereo_audio = stereo_audio + AudioSegment.silent(duration=1000)      
                
                #issue: reducing volume corrupts the audio, may be related to https://github.com/jiaaro/pydub/pull/781/commits                
                #stereo_audio = stereo_audio - 2                
                
                # Add the audio to the buffer queue
                buffer_queue.put(stereo_audio)

        await asyncio.sleep(0.1)  # Small delay to prevent busy waiting
        
# Main function to set up and run the audio streaming system
async def main(mode="time_weather"):
    kokoro = Kokoro("kokoro-v0_19.onnx", "voices.json")
    queue = asyncio.Queue()    

    if mode == "story":
        config = load_config()

        if config["story"] == "":
            story_file = choose_random_story("")
            config = init_new_story(story_file)

        if config["line"] > 1:
            opening_line = f"We now continue the story {config['title']}, by {config['author']}."
        else:
            opening_line = f"We now begin the tale '{config['title']}' by {config['author']}."

        await queue.put(opening_line)
        producer_task = asyncio.create_task(story_producer(queue))
    else:
        producer_task = asyncio.create_task(time_weather_producer(queue,"FOXR1")) # Providence, RI where Lovecraft lived
  
    consumer_task = asyncio.create_task(buffered_audio_consumer(queue, kokoro))        
    music_task = asyncio.create_task(background_music_player("audio/radio_background.mp3"))    
    
    start_input_thread(queue)

    await asyncio.gather(producer_task, consumer_task, music_task)
 

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run the radio streaming script.")
    parser.add_argument("--mode", type=str, default="time_weather", choices=["time_weather", "story"],
                        help="Set the mode of the script: 'time_weather' or 'story'.")
    
    args = parser.parse_args()

    try:
        asyncio.run(main(mode=args.mode))
    except KeyboardInterrupt:
        print("Program terminated by user")