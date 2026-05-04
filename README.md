# EmoBook

[![OpenVoice](https://img.shields.io/badge/Powered%20by-OpenVoiceV2-blue)](https://github.com/myshell-ai/OpenVoice)

EmoBook is an advanced voice cloning and emotional speech synthesis tool built on **OpenVoice V2**. It extracts speaker embeddings from your audio, generates expressive TTS speech from text, and clones your voice with high fidelity. Includes similarity evaluation and supports multi-lingual cloning.

## ✨ Features
- **Zero-shot Voice Cloning**: Clone any voice from a short audio sample.
- **Emotional Speech Synthesis**: Generate speech with controllable style/emotion (via OpenVoice).
- **Multi-lingual Support**: English, Spanish, French, Chinese, Japanese, Korean.
- **Similarity Evaluation**: Built-in cosine similarity score using Resemblyzer.
- **Easy Pipeline**: Single `run.py` for end-to-end: extract → generate → convert → evaluate.
- **MIT Licensed** (from OpenVoice V2): Free for commercial use.

## 🎯 Quick Start
1. **Setup Environment**:
   ```bash
   python -m venv emo_env
   source emo_env/bin/activate  # macOS/Linux
   # or emo_env\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

2. **Download Models**:
   ```bash
   python get.py
   ```

3. **Prepare Input**:
   Place your reference audio (`my_voice.wav`) in `data/input/`.

4. **Run Pipeline**:
   ```bash
   python run.py
   ```
   - Edits `TEXT` in `run.py` for custom speech.
   - Output: `data/output/cloned.wav`
   - Prints voice similarity score (closer to 1.0 = better clone).

**Example Output**:
```
Step 1: Extracting speaker embedding...
Step 2: Generating base speech...
Step 3: Converting to cloned voice...
Step 4: Evaluating similarity...
Voice similarity score: 0.9234
```

## 🛠️ Installation
### Prerequisites
- Python 3.9+
- macOS/Linux (MPS/CUDA supported via `get_device()`)
- ~2GB models in `checkpoints_v2/`

### Full Setup
```bash
git clone <this-repo>
cd EmoBook
python -m venv emo_env
source emo_env/bin/activate
pip install -r requirements.txt  # Includes OpenVoice, torch, librosa, etc.
python get.py  # Downloads OpenVoice V2 checkpoints
```

## 📁 Project Structure
```
EmoBook/
├── README.md              # This file
├── requirements.txt       # Dependencies
├── get.py                 # Download checkpoints
├── run.py                 # Main pipeline
├── app/
│   ├── extract.py         # Extract speaker embedding
│   ├── generate.py        # TTS base speech
│   ├── convert.py         # Tone color conversion/cloning
│   ├── util.py            # Device utils
│   └── tests/             # Unit tests
├── checkpoints_v2/        # OpenVoice V2 models (auto-download)
├── data/
│   ├── input/             # Reference WAVs (e.g., source.wav)
│   ├── processed/         # Extracted embeddings
│   └── output/            # Cloned WAVs
└── models/
    └── OpenVoice/         # Additional models
```

## 🔧 Customization
- **Change Text**: Edit `TEXT = "Your message here."` in `run.py`.
- **Reference Audio**: Add WAV to `data/input/`, update `INPUT_AUDIO`.
- **Emotion Control**: Modify params in `convert_voice()` (see OpenVoice docs).
- **Test Modules**:
  ```bash
  python app/test_extract.py
  python app/test_convert.py
  ```

## 📊 Evaluation
Uses Resemblyzer for embedding similarity:
```python
similarity = 1 - cosine(real_embedding, fake_embedding)
```
Higher score = better clone quality.

## Dependencies
See [requirements.txt](requirements.txt):
```
torch torchaudio librosa soundfile numpy scipy transformers accelerate resemblyzer
git+https://github.com/myshell-ai/OpenVoice.git
```

## 📄 License
MIT License (inherits from OpenVoice V2). See [LICENSE](checkpoints_v2/README.md) for details.


