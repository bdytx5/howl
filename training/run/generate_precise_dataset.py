import os
from pathlib import Path
from shutil import copyfile

import librosa
import numpy as np
from tqdm import tqdm

from howl.context import InferenceContext
from howl.data.dataset.dataset import DatasetType, WakeWordDataset
from howl.data.dataset.dataset_loader import RecursiveNoiseDatasetLoader, WakeWordDatasetLoader
from howl.data.transform.transform import DatasetMixer
from howl.settings import SETTINGS
from howl.utils.hash_utils import Sha256Splitter
from training.run.deprecated.create_raw_dataset import print_stats

from .args import ArgumentParserBuilder, opt


def main():
    """
    This script is used to transform datasets for howl to dataset for Mycroft-precise

    sample command:
    python -m training.run.generate_precise_dataset.py --i <datasets to convert> --o <location of the output dataset>
    """
    # TODO: generate_precise_dataset.py needs to be refactored
    # pylint: disable=too-many-statements

    def copy_files(dataset, output_dir, deep_copy=False):
        """Copy dataset to output dir"""
        print("copying files to", output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        for item in tqdm(dataset):
            output_path = output_dir / item.metadata.path.name
            try:
                if deep_copy:
                    copyfile(item.metadata.path, output_path)
                else:
                    os.symlink(item.metadata.path, output_path)
            except FileExistsError:
                pass

    def write_files(dataset, output_dir, mixer: DatasetMixer):
        """Write audio files of the given dataste to output dir"""
        print("Writing files to", output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        for item in tqdm(dataset):
            (item,) = mixer([item])
            output_path = output_dir / item.metadata.path.name
            librosa.output.write_wav(output_path, item.audio_data.numpy(), 16000)

    apb = ArgumentParserBuilder()
    apb.add_options(
        opt("--dataset-paths", "-i", type=str, nargs="+", default=[SETTINGS.dataset.dataset_path],),
        opt("--output-paths", "-o", type=str, default="data/precise"),
        opt("--deep-copy", action="store_true"),
    )
    args = apb.parser.parse_args()

    if args.deep_copy:
        print("copying the audio files")
    else:
        print("generating symlink files")

    use_frame = SETTINGS.training.objective == "frame"
    ctx = InferenceContext(SETTINGS.training.vocab, token_type=SETTINGS.training.token_type, use_blank=not use_frame,)

    loader = WakeWordDatasetLoader()
    ds_kwargs = dict(sample_rate=SETTINGS.audio.sample_rate, mono=SETTINGS.audio.use_mono, frame_labeler=ctx.labeler,)

    inference_settings = SETTINGS.inference_engine
    wakeword = "_".join(np.array(SETTINGS.training.vocab)[inference_settings.inference_sequence]).strip()

    ww_train_ds, ww_dev_ds, ww_test_ds = (
        WakeWordDataset(metadata_list=[], set_type=DatasetType.TRAINING, **ds_kwargs),
        WakeWordDataset(metadata_list=[], set_type=DatasetType.DEV, **ds_kwargs),
        WakeWordDataset(metadata_list=[], set_type=DatasetType.TEST, **ds_kwargs),
    )

    for ds_path in args.dataset_paths:
        ds_path = Path(ds_path)
        train_ds, dev_ds, test_ds = loader.load_splits(ds_path, **ds_kwargs)
        ww_train_ds.extend(train_ds)
        ww_dev_ds.extend(dev_ds)
        ww_test_ds.extend(test_ds)

    print_stats("Wake word dataset", ctx, ww_train_ds, ww_dev_ds, ww_test_ds)

    output_path = Path(args.output_paths) / wakeword

    ww_train_pos_ds = ww_train_ds.filter(lambda x: ctx.searcher.search(x.transcription), clone=True)
    print_stats("train positive dataset", ctx, ww_train_pos_ds)
    copy_files(ww_train_pos_ds, output_path / "wake-word", args.deep_copy)

    ww_train_neg_ds = ww_train_ds.filter(lambda x: not ctx.searcher.search(x.transcription), clone=True)
    print_stats("train negative dataset", ctx, ww_train_neg_ds)
    copy_files(ww_train_neg_ds, output_path / "not-wake-word", args.deep_copy)

    noise_ds = RecursiveNoiseDatasetLoader().load(
        Path(SETTINGS.training.noise_dataset_path),
        sample_rate=SETTINGS.audio.sample_rate,
        mono=SETTINGS.audio.use_mono,
    )
    _noise_ds_train, noise_ds_dev = noise_ds.split(Sha256Splitter(80))
    noise_ds_dev, noise_ds_test = noise_ds_dev.split(Sha256Splitter(50))

    dev_mixer = DatasetMixer(noise_ds_dev, seed=10, do_replace=False)
    test_mixer = DatasetMixer(noise_ds_test, seed=10, do_replace=False)

    ww_dev_pos_ds = ww_dev_ds.filter(lambda x: ctx.searcher.search(x.transcription), clone=True)
    print_stats("dev positive dataset", ctx, ww_dev_pos_ds)
    copy_files(ww_dev_pos_ds, output_path / "dev/wake-word", args.deep_copy)
    write_files(ww_dev_pos_ds, output_path / "noisy-dev/wake-word", dev_mixer)

    ww_dev_neg_ds = ww_dev_ds.filter(lambda x: not ctx.searcher.search(x.transcription), clone=True)
    print_stats("dev negative dataset", ctx, ww_dev_neg_ds)
    copy_files(ww_dev_neg_ds, output_path / "dev/not-wake-word", args.deep_copy)
    write_files(ww_dev_neg_ds, output_path / "noisy-dev/not-wake-word", dev_mixer)

    ww_test_pos_ds = ww_test_ds.filter(lambda x: ctx.searcher.search(x.transcription), clone=True)
    print_stats("test positive dataset", ctx, ww_test_pos_ds)
    copy_files(ww_test_pos_ds, output_path / "test/wake-word", args.deep_copy)
    write_files(ww_test_pos_ds, output_path / "noisy-test/wake-word", test_mixer)

    ww_test_neg_ds = ww_test_ds.filter(lambda x: not ctx.searcher.search(x.transcription), clone=True)
    print_stats("test negative dataset", ctx, ww_test_neg_ds)
    copy_files(ww_test_neg_ds, output_path / "test/not-wake-word", args.deep_copy)
    write_files(ww_test_neg_ds, output_path / "noisy-test/not-wake-word", test_mixer)


if __name__ == "__main__":
    main()
