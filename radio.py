import asyncio
import argparse
from kokoro_onnx import Kokoro
from radio.radio import Radio

async def main(mode):
    kokoro = Kokoro("kokoro-v0_19.onnx", "voices.json")
    radio = Radio(kokoro)
    await radio.run(mode)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the radio streaming script.")
    parser.add_argument("--mode", type=str, default="time_weather", choices=["time_weather", "story"],
                        help="Set the mode of the script: 'time_weather' or 'story'.")
    
    args = parser.parse_args()

    try:
        asyncio.run(main(mode=args.mode))
    except KeyboardInterrupt:
        print("Program terminated by user")
