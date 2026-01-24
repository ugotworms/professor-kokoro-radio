import unittest
import os
import shutil
from radio.story import Story

class TestStory(unittest.TestCase):
    def setUp(self):
        self.corpus_dir = "test_corpus"
        os.makedirs(self.corpus_dir, exist_ok=True)
        with open(os.path.join(self.corpus_dir, "story1.txt"), "w") as f:
            f.write("Title 1\nLine 1\nLine 2")
        with open(os.path.join(self.corpus_dir, "story2.txt"), "w") as f:
            f.write("Title 2\nLine 3\nLine 4")
        self.story = Story(self.corpus_dir)

    def tearDown(self):
        shutil.rmtree(self.corpus_dir)

    def test_choose_random_story_mock(self):
        story_file = self.story.choose_random_story(ignore="story1.txt")
        self.assertEqual(story_file, "story2.txt")

        story_file = self.story.choose_random_story(ignore="story2.txt")
        self.assertEqual(story_file, "story1.txt")

    def test_init_new_story(self):
        config = {}
        story_file = "story1.txt"
        new_config = self.story.init_new_story(story_file, config)
        self.assertEqual(new_config["title"], "Title 1")
        self.assertEqual(new_config["line"], 1)
        self.assertEqual(new_config["story"], story_file)

    def test_load_corpus_lines(self):
        story_file = "story1.txt"
        with open(os.path.join(self.corpus_dir, story_file), "w") as f:
            f.write("Title 1\nLine 1\nCthulhu--fhtagn")

        lines = self.story.load_corpus_lines(story_file)
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[0], "Line 1")
        self.assertEqual(lines[1], "kuh-thewloo, fhtagn")

    def test_correct_pronunciation(self):
        text = "Miskatonic Arkham Cthulhu R'lyeh Nyarlathotep Yog-Sothoth Pnakotic--"
        corrected_text = self.story.correct_pronunciation(text)
        self.assertEqual(corrected_text, "miss-kuh-tonic ark-hum kuh-thewloo rill-ee-uh nye-are-lath-oh-tep yog-so-thoth nuh-kah-tick, ")

if __name__ == "__main__":
    unittest.main()
