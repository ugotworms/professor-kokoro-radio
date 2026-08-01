import os
import random

class Story:
    def __init__(self, corpus_dir="corpus"):
        self.corpus_dir = corpus_dir

    def choose_random_story(self, ignore):
        corpus_files = [f for f in os.listdir(self.corpus_dir) if f != ignore and os.path.isfile(os.path.join(self.corpus_dir, f))]
        random_story = random.choice(corpus_files)
        return random_story

    def init_new_story(self, story_file, config):
        with open(os.path.join(self.corpus_dir, story_file), "r") as f:
            lines = f.readlines()
        config["title"] = lines[0].strip()
        config["line"] = 1
        config["story"] = f"{story_file}"
        return config

    def load_corpus_lines(self, story_file):
        with open(os.path.join(self.corpus_dir, story_file), "r") as f:
            lines = f.readlines()
        # Remove blank/empty lines and convert unique Lovecraftian words to phonetic spelling
        lines = [self.correct_pronunciation(line.strip()) for line in lines if line.strip()]
        return lines[1:]

    def correct_pronunciation(self, text):
        text = text.replace("Miskatonic", "miss-kuh-tonic")
        text = text.replace("Arkham", "ark-hum")
        text = text.replace("Cthulhu", "kuh-thewloo")
        #text = text.replace("Necronomicon", "neck-row-nom-ih-con")
        text = text.replace("R'lyeh", "rill-ee-uh")
        text = text.replace("Nyarlathotep", "nye-are-lath-oh-tep")
        text = text.replace("Yog-Sothoth", "yog-so-thoth")
        text = text.replace("Pnakotic", "nuh-kah-tick")
        text = text.replace("--", ", ")
        return text
