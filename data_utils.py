import os
import random
import numpy as np
import torch
import torch.utils.data
from pathlib import Path

import commons
from mel_processing import spectrogram_torch
from utils import load_wav_to_torch, load_filepaths_and_text
from text import text_to_sequence, cleaned_text_to_sequence


class PPGAudioSpeakerLoader(torch.utils.data.Dataset):

    def __init__(self, audiopaths_sid_text, hparams):
        self.audiopaths_sid_text = load_filepaths_and_text(audiopaths_sid_text)
        self.max_wav_value = hparams.max_wav_value
        self.sampling_rate = hparams.sampling_rate
        self.filter_length = hparams.filter_length
        self.hop_length = hparams.hop_length
        self.win_length = hparams.win_length
        self.sampling_rate = hparams.sampling_rate
        self.interp_method = hparams.interp_method

        random.seed(1234)
        random.shuffle(self.audiopaths_sid_text)

        # Store spectrogram lengths for bucketing
        self.lengths = [
            os.path.getsize(path) // (2 * self.hop_length)
            for path, _, _ in self.audiopaths_sid_text]

    def get_audio_ppg_speaker_pair(self, audiopath_sid_text):
        # Separate filenames and speaker_id
        audiopath, sid, text = audiopath_sid_text
        spec, wav = self.get_audio(audiopath)
        ppgpath = Path(audiopath).parent / f'{Path(audiopath).stem}-ppg.npy'
        ppg = self.get_ppg(ppgpath, spec.shape[1])
        sid = torch.LongTensor([int(sid)])
        return (ppg, spec, wav, sid)

    def get_audio(self, filename):
        audio, sampling_rate = load_wav_to_torch(filename)
        if sampling_rate != self.sampling_rate:
            raise ValueError("{} {} SR doesn't match target {} SR".format(
                sampling_rate, self.sampling_rate))
        audio_norm = audio / self.max_wav_value
        audio_norm = audio_norm.unsqueeze(0)
        spec_filename = filename.replace(".wav", ".spec.pt")
        if os.path.exists(spec_filename):
            spec = torch.load(spec_filename)
        else:
            spec = spectrogram_torch(audio_norm, self.filter_length,
                                     self.sampling_rate, self.hop_length, self.win_length,
                                     center=False)
            spec = torch.squeeze(spec, 0)
            torch.save(spec, spec_filename)
        return spec, audio_norm

    def get_ppg(self, filename, length):
        """Load PPG features"""
        ppg = torch.from_numpy(np.load(filename))

        # Maybe resample length
        if ppg.shape[1] != length:
            ppg = torch.nn.functional.interpolate(
                ppg[None],
                size=length,
                mode=self.interp_method)[0]

        return ppg

    def __getitem__(self, index):
        return self.get_audio_ppg_speaker_pair(self.audiopaths_sid_text[index])

    def __len__(self):
        return len(self.audiopaths_sid_text)


class PPGAudioSpeakerCollate():

    def __call__(self, batch):
        """Collates training batch from ppg, audio and speaker identities
        PARAMS
        ------
        batch: [ppg, spec_normalized, wav_normalized, sid]
        """
        ppg, spec, wav, sid = zip(*batch)

        # Right zero-pad all one-hot text sequences to max input length
        _, ids_sorted_decreasing = torch.sort(
            torch.LongTensor([x[1].size(1) for x in batch]),
            dim=0, descending=True)

        max_ppg_len = max([x[0].size(1) for x in batch])
        max_spec_len = max([x[1].size(1) for x in batch])
        max_wav_len = max([x[2].size(1) for x in batch])

        ppg_lengths = torch.LongTensor(len(batch))
        spec_lengths = torch.LongTensor(len(batch))
        wav_lengths = torch.LongTensor(len(batch))
        sid = torch.LongTensor(len(batch))

        ppg_padded = torch.FloatTensor(len(batch), ppg[0].size(0), max_ppg_len)
        spec_padded = torch.FloatTensor(
            len(batch), spec[0].size(0), max_spec_len)
        wav_padded = torch.FloatTensor(len(batch), 1, max_wav_len)
        ppg_padded.zero_()
        spec_padded.zero_()
        wav_padded.zero_()
        for i in range(len(ids_sorted_decreasing)):
            row = batch[ids_sorted_decreasing[i]]

            ppg = row[0]
            ppg_padded[i, :, :ppg.size(1)] = ppg
            ppg_lengths[i] = ppg.size(1)

            spec = row[1]
            spec_padded[i, :, :spec.size(1)] = spec
            spec_lengths[i] = spec.size(1)

            wav = row[2]
            wav_padded[i, :, :wav.size(1)] = wav
            wav_lengths[i] = wav.size(1)

            sid[i] = row[3]

        return ppg_padded, ppg_lengths, spec_padded, spec_lengths, wav_padded, wav_lengths, sid


"""Multi speaker version"""
class TextAudioSpeakerLoader(torch.utils.data.Dataset):
    """
        1) loads audio, speaker_id, text pairs
        2) normalizes text and converts them to sequences of integers
        3) computes spectrograms from audio files.
    """
    def __init__(self, audiopaths_sid_text, hparams):
        self.audiopaths_sid_text = load_filepaths_and_text(audiopaths_sid_text)
        self.text_cleaners = hparams.text_cleaners
        self.max_wav_value = hparams.max_wav_value
        self.sampling_rate = hparams.sampling_rate
        self.filter_length  = hparams.filter_length
        self.hop_length     = hparams.hop_length
        self.win_length     = hparams.win_length
        self.sampling_rate  = hparams.sampling_rate

        self.cleaned_text = getattr(hparams, "cleaned_text", False)

        self.add_blank = hparams.add_blank
        self.min_text_len = getattr(hparams, "min_text_len", 1)
        self.max_text_len = getattr(hparams, "max_text_len", 190)

        random.seed(1234)
        random.shuffle(self.audiopaths_sid_text)
        self._filter()

    def _filter(self):
        """
        Filter text & store spec lengths
        """
        # Store spectrogram lengths for Bucketing
        # wav_length ~= file_size / (wav_channels * Bytes per dim) = file_size / (1 * 2)
        # spec_length = wav_length // hop_length

        audiopaths_sid_text_new = []
        lengths = []
        for audiopath, sid, text in self.audiopaths_sid_text:
            if self.min_text_len <= len(text) and len(text) <= self.max_text_len:
                audiopaths_sid_text_new.append([audiopath, sid, text])
                lengths.append(os.path.getsize(audiopath) // (2 * self.hop_length))
        self.audiopaths_sid_text = audiopaths_sid_text_new
        self.lengths = lengths

    def get_audio_text_speaker_pair(self, audiopath_sid_text):
        # separate filename, speaker_id and text
        audiopath, sid, text = audiopath_sid_text[0], audiopath_sid_text[1], audiopath_sid_text[2]
        text = self.get_text(text)
        spec, wav = self.get_audio(audiopath)
        sid = self.get_sid(sid)
        return (text, spec, wav, sid)

    def get_audio(self, filename):
        audio, sampling_rate = load_wav_to_torch(filename)
        if sampling_rate != self.sampling_rate:
            raise ValueError("{} {} SR doesn't match target {} SR".format(
                sampling_rate, self.sampling_rate))
        audio_norm = audio / self.max_wav_value
        audio_norm = audio_norm.unsqueeze(0)
        spec_filename = filename.replace(".wav", ".spec.pt")
        if os.path.exists(spec_filename):
            spec = torch.load(spec_filename)
        else:
            spec = spectrogram_torch(audio_norm, self.filter_length,
                self.sampling_rate, self.hop_length, self.win_length,
                center=False)
            spec = torch.squeeze(spec, 0)
            torch.save(spec, spec_filename)
        return spec, audio_norm

    def get_text(self, text):
        if self.cleaned_text:
            text_norm = cleaned_text_to_sequence(text)
        else:
            text_norm = text_to_sequence(text, self.text_cleaners)
        if self.add_blank:
            text_norm = commons.intersperse(text_norm, 0)
        text_norm = torch.LongTensor(text_norm)
        return text_norm

    def get_sid(self, sid):
        sid = torch.LongTensor([int(sid)])
        return sid

    def __getitem__(self, index):
        return self.get_audio_text_speaker_pair(self.audiopaths_sid_text[index])

    def __len__(self):
        return len(self.audiopaths_sid_text)


class TextAudioSpeakerCollate():
    """ Zero-pads model inputs and targets
    """
    def __call__(self, batch):
        """Collate's training batch from normalized text, audio and speaker identities
        PARAMS
        ------
        batch: [text_normalized, spec_normalized, wav_normalized, sid]
        """
        # Right zero-pad all one-hot text sequences to max input length
        _, ids_sorted_decreasing = torch.sort(
            torch.LongTensor([x[1].size(1) for x in batch]),
            dim=0, descending=True)

        max_text_len = max([len(x[0]) for x in batch])
        max_spec_len = max([x[1].size(1) for x in batch])
        max_wav_len = max([x[2].size(1) for x in batch])

        text_lengths = torch.LongTensor(len(batch))
        spec_lengths = torch.LongTensor(len(batch))
        wav_lengths = torch.LongTensor(len(batch))
        sid = torch.LongTensor(len(batch))

        text_padded = torch.LongTensor(len(batch), max_text_len)
        spec_padded = torch.FloatTensor(len(batch), batch[0][1].size(0), max_spec_len)
        wav_padded = torch.FloatTensor(len(batch), 1, max_wav_len)
        text_padded.zero_()
        spec_padded.zero_()
        wav_padded.zero_()
        for i in range(len(ids_sorted_decreasing)):
            row = batch[ids_sorted_decreasing[i]]

            text = row[0]
            text_padded[i, :text.size(0)] = text
            text_lengths[i] = text.size(0)

            spec = row[1]
            spec_padded[i, :, :spec.size(1)] = spec
            spec_lengths[i] = spec.size(1)

            wav = row[2]
            wav_padded[i, :, :wav.size(1)] = wav
            wav_lengths[i] = wav.size(1)

            sid[i] = row[3]

        return text_padded, text_lengths, spec_padded, spec_lengths, wav_padded, wav_lengths, sid


###############################################################################
# Samplers
###############################################################################


class BucketSampler(torch.utils.data.Sampler):

    def __init__(
        self,
        dataset,
        batch_size,
        boundaries):
        super().__init__(dataset)
        self.batch_size = batch_size
        self.boundaries = boundaries
        self.buckets, self.samples_per_bucket = self.create_buckets(
            dataset.lengths,
            boundaries,
            batch_size)
        self.total_size = sum(self.samples_per_bucket)

    def __iter__(self):
        self.batches = make_batches(
            self.buckets,
            self.samples_per_bucket,
            self.batch_size,
            self.epoch,
            False)
        return iter(self.batches)

    def __len__(self):
        """Retrieve the number of batches in an epoch"""
        return self.total_size // self.batch_size

    def set_epoch(self, epoch):
        self.epoch = epoch


class DistributedBucketSampler(torch.utils.data.distributed.DistributedSampler):
    """
    Maintain similar input lengths in a batch.
    Length groups are specified by boundaries.
    Ex) boundaries = [b1, b2, b3] -> any batch is included either {x | b1 < length(x) <=b2} or {x | b2 < length(x) <= b3}.

    It removes samples which are not included in the boundaries.
    Ex) boundaries = [b1, b2, b3] -> any x s.t. length(x) <= b1 or length(x) > b3 are discarded.
    """
    def __init__(
        self,
        dataset,
        batch_size,
        boundaries,
        num_replicas=None,
        rank=None,
        shuffle=True):
        super().__init__(
            dataset,
            num_replicas=num_replicas,
            rank=rank,
            shuffle=shuffle)
        self.batch_size = batch_size
        self.boundaries = boundaries
        self.buckets, self.samples_per_bucket = create_buckets(
            dataset.lengths,
            boundaries,
            batch_size,
            num_replicas)
        self.total_size = sum(self.samples_per_bucket)
        self.num_samples = self.total_size // self.num_replicas

    def __iter__(self):
      self.batches = make_batches(
          self.buckets,
          self.samples_per_bucket,
          self.batch_size,
          self.epoch,
          self.shuffle,
          self.rank,
          self.num_replicas)
      return iter(self.batches)

    def __len__(self):
        return self.num_samples // self.batch_size


class RandomBucketSampler(torch.utils.data.RandomSampler):

    def __init__(
            self,
            dataset,
            batch_size,
            boundaries):
        super().__init__(dataset)
        self.batch_size = batch_size
        self.boundaries = boundaries
        self.buckets, self.samples_per_bucket = create_buckets(
            dataset.lengths,
            boundaries,
            batch_size)
        self.total_size = sum(self.samples_per_bucket)

    def __iter__(self):
        self.batches = make_batches(
            self.buckets,
            self.samples_per_bucket,
            self.batch_size,
            self.epoch)
        return iter(self.batches)

    def __len__(self):
        """Retrieve the number of batches in an epoch"""
        return self.total_size // self.batch_size

    def set_epoch(self, epoch):
        self.epoch = epoch


###############################################################################
# Sampler utilities
###############################################################################


def bisect(x, boundaries, lo=0, hi=None):
    if hi is None:
        hi = len(boundaries) - 1

    if hi > lo:
        mid = (hi + lo) // 2
        if boundaries[mid] < x and x <= boundaries[mid+1]:
            return mid
        elif x <= boundaries[mid]:
            return bisect(x, boundaries, lo, mid)
        else:
            return bisect(x, boundaries, mid + 1, hi)
    return -1


def create_buckets(lengths, boundaries, batch_size, num_replicas=1):
    buckets = [[] for _ in range(len(boundaries) - 1)]
    for i in range(len(lengths)):
        length = lengths[i]
        idx_bucket = bisect(length, boundaries)
        if idx_bucket != -1:
            buckets[idx_bucket].append(i)

    for i in range(len(buckets) - 1, 0, -1):
        if len(buckets[i]) == 0:
            buckets.pop(i)
            boundaries.pop(i+1)

    samples_per_bucket = []
    for i in range(len(buckets)):
        len_bucket = len(buckets[i])
        total_batch_size = num_replicas * batch_size
        rem = (total_batch_size - (len_bucket %
                total_batch_size)) % total_batch_size
        samples_per_bucket.append(len_bucket + rem)
    return buckets, samples_per_bucket


def make_batches(
    buckets,
    samples_per_bucket,
    batch_size,
    epoch,
    shuffle=True,
    rank=None,
    num_replicas=None):
    # Deterministic shuffling based on current epoch
    g = torch.Generator()
    g.manual_seed(epoch)

    indices = []
    if shuffle:
        for bucket in buckets:
            indices.append(torch.randperm(len(bucket), generator=g).tolist())
    else:
        for bucket in buckets:
            indices.append(list(range(len(bucket))))

    batches = []
    for i in range(len(buckets)):
        bucket = buckets[i]
        len_bucket = len(bucket)
        ids_bucket = indices[i]
        num_samples_bucket = samples_per_bucket[i]

        # Add extra samples to make it evenly divisible
        rem = num_samples_bucket - len_bucket
        ids_bucket = ids_bucket + ids_bucket * \
            (rem // len_bucket) + ids_bucket[:(rem % len_bucket)]

        # Subsample
        ids_bucket = ids_bucket[rank::num_replicas]

        # Batch
        for j in range(len(ids_bucket) // batch_size):
            batch = [bucket[idx]
                     for idx in ids_bucket[j*batch_size:(j+1)*batch_size]]
            batches.append(batch)

    if shuffle:
        batch_ids = torch.randperm(len(batches), generator=g).tolist()
        batches = [batches[i] for i in batch_ids]

    return batches
