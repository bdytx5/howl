from typing import List

from howl.data.common.vocab import Vocab

__all__ = ["WakeWordTokenizer", "TranscriptTokenizer"]


class TranscriptTokenizer:
    def encode(self, transcript: str) -> List[int]:
        raise NotImplementedError

    def decode(self, ids: List[int]) -> str:
        raise NotImplementedError


class WakeWordTokenizer(TranscriptTokenizer):
    # Only used for ctc objective
    def __init__(self, vocab: Vocab, ignore_oov: bool = True):
        self.vocab = vocab
        self.ignore_oov = ignore_oov

    def decode(self, ids: List[int]) -> str:
        return " ".join(self.vocab[id] for id in ids)

    def encode(self, transcript: str) -> List[int]:
        encoded_output = []

        for word in transcript.lower().split():
            vocab_found, remaining_transcript = self.vocab.trie.max_split(word)

            # append corresponding label
            if vocab_found and remaining_transcript == "":
                # word exists in the vocab
                encoded_output.append(self.vocab[word])
            elif not self.ignore_oov:
                # label oov word
                if self.vocab.oov_token_id is None:
                    raise ValueError("label for oov word is not specified")
                encoded_output.append(self.vocab.oov_token_id)

        return encoded_output
