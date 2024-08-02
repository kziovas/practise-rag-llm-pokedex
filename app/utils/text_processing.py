import nltk
from nltk.tokenize import sent_tokenize, word_tokenize


class _TextProcessing:
    def __init__(self):
        nltk.download("punkt")  # Ensure NLTK's Punkt tokenizer is downloaded

    def truncate_text(self, text, max_sentences=5, max_words=50):
        # Tokenize the text into sentences
        sentences = sent_tokenize(text.strip())

        # Initialize counters
        word_count = 0
        truncated_text = []

        # Iterate through sentences
        for sentence in sentences:
            # Tokenize each sentence into words
            words = word_tokenize(sentence)

            # Count words in the current sentence
            sentence_word_count = len(words)

            # Check if adding this sentence exceeds word limit or if sentence count exceeds max_sentences
            if (
                word_count + sentence_word_count > max_words
                or len(truncated_text) >= max_sentences
            ):
                break

            # Append sentence
            truncated_text.append(sentence)
            word_count += sentence_word_count

        # Return the truncated text
        return " ".join(truncated_text)


# Singleton instance
TextProcessing = _TextProcessing()
