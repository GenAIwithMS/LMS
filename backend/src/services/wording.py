# Small helpers for messages people read.


def plural(count, word, word_plural=None):
    """ "1 paper", "3 papers" (or a special plural: "2 diary entries")."""
    if count == 1:
        return f"1 {word}"
    if word_plural is None:
        word_plural = word + "s"
    return f"{count} {word_plural}"
