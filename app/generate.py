import torch
import soundfile as sf
from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq
from app.utils import get_device

device = get_device()

MODEL_NAME = "Qwen/Qwen3-TTS"

def generate_speech(text, output_path="data/output/base.wav"):
    processor = AutoProcessor.from_pretrained(MODEL_NAME)
    model = AutoModelForSpeechSeq2Seq.from_pretrained(MODEL_NAME).to(device)

    inputs = processor(text=text, return_tensors="pt").to(device)

    with torch.no_grad():
        speech = model.generate(**inputs)

    audio = speech.cpu().numpy().squeeze()

    sf.write(output_path, audio, 22050)

    return output_path