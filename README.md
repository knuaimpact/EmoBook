# EmoBook

EmoBook is a Korean voice-cloning toolkit for generating speech from a
reference voice sample. The current workflow uses OpenVoice V2 for tone-color
conversion and MeloTTS for Korean base speech synthesis.

Primary output language:

- Korean

## Project Structure

```text
.
├── scripts/
│   └── openvoice_v2_multilang_clone.py
├── docs/
│   └── openvoice_v2_multilang_clone.md
├── OpenVoice/
│   └── openvoice/
├── MeloTTS/
│   └── melo/
└── transcript.v.1.4.txt
```

`OpenVoice` and `MeloTTS` are included as local third-party engines so the
project can run without depending on a separate source checkout.

## Quick Start

Create a clean Python environment first. Python 3.9 is recommended because the
third-party dependencies are pinned around that version.

```bash
conda create -n emobook python=3.9
conda activate emobook
```

Install PyTorch for your machine, then install the local engines:

```bash
pip install torch torchaudio
python scripts/openvoice_v2_multilang_clone.py --install-deps
```

Download OpenVoice V2 checkpoints:

```bash
python scripts/openvoice_v2_multilang_clone.py --download-checkpoints
```

Generate cloned speech:

```bash
python scripts/openvoice_v2_multilang_clone.py \
  --reference-audio /path/to/reference.wav \
  --texts-json examples/test_texts_ko.json \
  --output-dir outputs/sample_voice \
  --languages kr
```

See [docs/openvoice_v2_multilang_clone.md](docs/openvoice_v2_multilang_clone.md)
for detailed usage and troubleshooting.

## Text Input

Korean text input uses this format:

```json
{
  "kr": "안녕하세요, 이것은 EmoBook 한국어 음성 복제 테스트입니다."
}
```

## Notes

- Generated audio and downloaded model checkpoints are ignored by Git.
- Keep reference voice samples clear, dry, and at least 10 seconds long.
- Use voice samples only when you have the right to clone that speaker's voice.

## Third-Party Components

This project includes third-party code from:

- OpenVoice by MyShell
- MeloTTS by MyShell

Their original license files are preserved in `OpenVoice/LICENSE` and
`MeloTTS/LICENSE`. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
