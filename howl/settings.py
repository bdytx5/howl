from typing import List

from pydantic import BaseSettings

__all__ = ["AudioSettings", "DatasetSettings", "SETTINGS"]


class CacheSettings(BaseSettings):
    """Base settings for cache"""

    cache_size: int = 128144


class AudioSettings(BaseSettings):
    """Base settings for audio"""

    sample_rate: int = 16000
    use_mono: bool = True


class AudioTransformSettings(BaseSettings):
    """Base settings for audio transform"""

    num_fft: int = 512
    num_mels: int = 80
    sample_rate: int = 16000
    hop_length: int = 200
    use_meyda_spectrogram: bool = False


class InferenceEngineSettings(BaseSettings):
    """Base settings for inference engine"""

    inference_weights: List[float] = None
    inference_sequence: List[int] = [0]
    inference_window_ms: float = 2000  # look at last of these seconds
    smoothing_window_ms: float = 50  # prediction smoothed
    tolerance_window_ms: float = 500  # negative label between words
    inference_threshold: float = 0  # positive label probability must rise above this threshold


class TrainingSettings(BaseSettings):
    """Base settings for training"""

    seed: int = 0
    # TODO:: vocab should not belong to training
    vocab: List[str] = ["fire"]
    num_epochs: int = 10
    num_labels: int = 2
    learning_rate: float = 1e-3
    device: str = "cuda:0"
    batch_size: int = 16
    lr_decay: float = 0.75
    max_window_size_seconds: float = 0.75
    eval_window_size_seconds: float = 0.75
    eval_stride_size_seconds: float = 0.063
    weight_decay: float = 0
    convert_static: bool = False
    objective: str = "frame"  # frame or ctc
    # TODO: support phone token_type
    token_type: str = "word"
    phone_dictionary: str = None
    use_noise_dataset: bool = False
    noise_dataset_path: str = None


class DatasetSettings(BaseSettings):
    """Base settings for dataset"""

    dataset_path: str = None


class HowlSettings:
    """Lazy-loaded class containing all required settings"""

    _audio: AudioSettings = None
    _audio_transform: AudioTransformSettings = None
    _inference_engine: InferenceEngineSettings = None
    _dataset: DatasetSettings = None
    _cache: CacheSettings = None
    _training: TrainingSettings = None

    @property
    def audio(self) -> AudioSettings:
        """audio settings"""
        if self._audio is None:
            self._audio = AudioSettings()
        return self._audio

    @property
    def audio_transform(self) -> AudioTransformSettings:
        """audio transform settings"""
        if self._audio_transform is None:
            self._audio_transform = AudioTransformSettings()
        return self._audio_transform

    @property
    def inference_engine(self) -> InferenceEngineSettings:
        """inference engine settings"""
        if self._inference_engine is None:
            self._inference_engine = InferenceEngineSettings()
        return self._inference_engine

    @property
    def dataset(self) -> DatasetSettings:
        """dataset settings"""
        if self._dataset is None:
            self._dataset = DatasetSettings()
        return self._dataset

    @property
    def cache(self) -> CacheSettings:
        """cache settings"""
        if self._cache is None:
            self._cache = CacheSettings()
        return self._cache

    @property
    def training(self) -> TrainingSettings:
        """training settings"""
        if self._training is None:
            self._training = TrainingSettings()
        return self._training


KEY_TO_SETTINGS_CLASS = {
    "_audio": AudioSettings,
    "_audio_transform": AudioTransformSettings,
    "_inference_engine": InferenceEngineSettings,
    "_dataset": DatasetSettings,
    "_cache": CacheSettings,
    "_training": TrainingSettings,
}

SETTINGS = HowlSettings()
