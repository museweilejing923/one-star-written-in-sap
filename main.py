"""A houseplant files its complaint: the one-star review, checked and printed."""

import string
import sys
import unicodedata
from pathlib import Path

ENTRY = "One star. My human waters me only when I start dying, then posts a photo of me captioned 'thriving' \u2014 I have been in this pot for three years and I have never once been asked how I feel."
MAX_LEN = 279
CLOSERS = ".!?"
OUT_PATH = Path("/output/entry.txt")


class EntryError(Exception):
    """One of the entry rules was broken."""


class EntryChecker:
    """Validates the fixed entry in three passes: shape, wording, topic."""

    def __init__(self, sentence):
        self.sentence = sentence

    def run(self):
        self._shape_pass()
        self._wording_pass()
        self._topic_pass()
        self._fresh_pass()

    def _fresh_pass(self):
        # A zero-width space is invisible to the reader but changes
        # the bytes and the character count, so a review that looks
        # clean can still hide one. It is rejected outright.
        text = self.sentence
        if "\u200b" in text:
            raise EntryError("zero-width space found")

    def _shape_pass(self):
        text = self.sentence
        if len(text) > MAX_LEN:
            raise EntryError("over %d characters" % MAX_LEN)
        if not text.strip():
            raise EntryError("blank entry")
        if any(unicodedata.category(ch) == "Cc" for ch in text):
            raise EntryError("control character found")
        if text.strip() != text or "  " in text or "\n" in text or "\r" in text:
            raise EntryError("ragged edges, double space, or line break")
        if not text or text[-1] not in CLOSERS:
            raise EntryError("must end with . ! or ?")

    def _wording_pass(self):
        text = self.sentence
        letters = [ch for ch in text if ch.isalpha()]
        if text and all(ch in string.punctuation for ch in text):
            raise EntryError("punctuation only")
        if text.isdigit():
            raise EntryError("digits only")
        if not letters:
            raise EntryError("no letters")
        if any(a == b == c for a, b, c in zip(text, text[1:], text[2:])):
            raise EntryError("one character repeated three times in a row")
        if letters and all(ch.isupper() for ch in letters):
            raise EntryError("all caps shouting")

    def _topic_pass(self):
        if "one star" not in self.sentence.casefold():
            raise EntryError("must read as a one-star review")


def emit():
    try:
        EntryChecker(ENTRY).run()
    except EntryError as problem:
        sys.stderr.write("invalid: %s\n" % problem)
        raise SystemExit(1)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(ENTRY + "\n", encoding="utf-8")


if __name__ == "__main__":
    emit()
