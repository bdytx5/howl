from pathlib import Path

import torch

import howl
from howl.data.common.example import AudioClipExample
from howl.data.common.metadata import AudioClipMetadata
from howl.data.dataset.dataset import AudioDataset
from howl.utils.audio import silent_load


def test_data_path():
    """Test data folder path"""
    return howl.root_path() / "test/test_data"


def common_voice_dataset_path():
    """Test common voice dataset folder path"""
    return test_data_path() / "dataset/common-voice"


def raw_audio_datasets_path():
    """Test raw audio dataset folder path"""
    return test_data_path() / "dataset/raw_audio_datasets"


def get_num_of_lines(file_path: Path):
    """Get number of lines in the given file path"""
    return sum(1 for _ in open(file_path))


class TestDataset(AudioDataset[AudioClipMetadata]):
    """Sample dataset for testing"""

    __test__ = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        test_common_voice_dataset_path = common_voice_dataset_path()
        metadata1 = AudioClipMetadata(
            transcription="The applicants are invited for coffee and visa is given immediately.",
            path=test_common_voice_dataset_path / "clips/common_voice_en_20005954.mp3",
        )
        audio_data = torch.from_numpy(silent_load(str(metadata1.path), self.sample_rate, self.mono))
        sample1 = AudioClipExample(metadata=metadata1, audio_data=audio_data, sample_rate=self.sample_rate)

        metadata2 = AudioClipMetadata(
            transcription="The anticipated synergies of the two modes of transportation were entirely absent.",
            path=test_common_voice_dataset_path / "clips/common_voice_en_20009653.mp3",
        )
        audio_data = torch.from_numpy(silent_load(str(metadata2.path), self.sample_rate, self.mono))
        sample2 = AudioClipExample(metadata=metadata2, audio_data=audio_data, sample_rate=self.sample_rate)

        metadata3 = AudioClipMetadata(
            transcription="The fossil fuels include coal, petroleum and natural gas.",
            path=test_common_voice_dataset_path / "clips/common_voice_en_20009655.mp3",
        )
        audio_data = torch.from_numpy(silent_load(str(metadata3.path), self.sample_rate, self.mono))
        sample3 = AudioClipExample(metadata=metadata3, audio_data=audio_data, sample_rate=self.sample_rate)

        self.samples = [sample1, sample2, sample3]
        self.metadata_list = [metadata1, metadata2, metadata3]

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx) -> AudioClipExample:
        return self.samples[idx]
