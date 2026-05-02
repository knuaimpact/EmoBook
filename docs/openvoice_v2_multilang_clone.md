# EmoBook Korean Voice Cloning

EmoBook includes local `OpenVoice` and `MeloTTS` third-party engines. The script
at `scripts/openvoice_v2_multilang_clone.py` generates Korean base speech
with MeloTTS, extracts the target speaker embedding from a reference sample, and
converts the base speech into that voice with OpenVoice V2.

## Installation

1. Create and activate a Python environment. Python 3.9 is the safest choice for
   the pinned OpenVoice dependencies.

   ```bash
   conda create -n emobook python=3.9
   conda activate emobook
   ```

2. Install PyTorch for your machine from the official PyTorch selector. Example
   CPU install:

   ```bash
   pip install torch torchaudio
   ```

3. Install local OpenVoice and MeloTTS packages, then download the Japanese
   dictionary used by MeloTTS:

   ```bash
   python scripts/openvoice_v2_multilang_clone.py --install-deps
   ```

4. Download the official OpenVoice V2 checkpoints:

   ```bash
   python scripts/openvoice_v2_multilang_clone.py --download-checkpoints
   ```

   The checkpoints are stored by default in `OpenVoice/checkpoints_v2`.

## Example Usage

Generate Korean speech using the sample Korean text:

```bash
python scripts/openvoice_v2_multilang_clone.py \
  --reference-audio /path/to/reference.wav \
  --texts-json examples/test_texts_ko.json \
  --output-dir outputs/ko_test \
  --languages kr
```

Generate Korean speech using one supplied text string:

```bash
python scripts/openvoice_v2_multilang_clone.py \
  --reference-audio /path/to/person.wav \
  --text "안녕하세요, 이것은 한국어 테스트입니다." \
  --output-dir outputs/person_01 \
  --languages kr
```

For repeatable testing, pass Korean text with JSON:

```json
{
  "kr": "안녕하세요, 이것은 테스트입니다."
}
```

```bash
python scripts/openvoice_v2_multilang_clone.py \
  --reference-audio /path/to/person.wav \
  --texts-json examples/test_texts_ko.json \
  --output-dir outputs/person_01 \
  --languages kr
```

Force CPU or GPU explicitly:

```bash
python scripts/openvoice_v2_multilang_clone.py \
  --reference-audio /path/to/person.wav \
  --device cpu
```

```bash
python scripts/openvoice_v2_multilang_clone.py \
  --reference-audio /path/to/person.wav \
  --device cuda:0
```

## Troubleshooting

- Model download fails: rerun with `--download-checkpoints`; if the S3 download
  is interrupted, add `--force-download`. MeloTTS base models are downloaded from
  Hugging Face on first use, so network access is also needed during generation.
- `ffmpeg` or audio decoding errors: install ffmpeg, and convert unusual formats
  to mono WAV first: `ffmpeg -i input.m4a -ac 1 -ar 16000 reference.wav`.
- Very short reference samples: use a clear 10-30 second sample with minimal
  background noise. The VAD splitter can fail on silent or noisy clips.
- CUDA out of memory: use `--device cpu`, shorten text, or generate fewer
  samples.
- Korean G2P/MeCab issues: the project includes a conservative Korean fallback
  so Korean smoke tests can still run in constrained local environments.
- Python dependency conflicts: use Python 3.9 in a fresh environment. The local
  OpenVoice package pins older versions such as `numpy==1.22.0`.
