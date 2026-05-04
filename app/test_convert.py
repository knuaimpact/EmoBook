from openvoice.api import ToneColorConverter
import torch

# paths
config_path = "checkpoints_v2/converter/config.json"
checkpoint_path = "checkpoints_v2/converter/checkpoint.pth"

source_audio = "data/input/source.wav"
output_audio = "data/output/cloned.wav"

# load model
converter = ToneColorConverter(config_path=config_path, device="cpu")
converter.load_ckpt(checkpoint_path)

# load your embedding (from previous step)
embedding = torch.load("data/processed/my_voice_v2_bDdPciamo6E8Ajge/se.pth")

print("Starting conversion...")

# convert voice
audio = converter.convert(
    audio_src_path=source_audio,
    src_se=embedding, # use None when input other people voice the voiceto be clone to
    tgt_se=embedding
)

# save output
import soundfile as sf
sf.write(output_audio, audio, 22050)

print("✅ Voice cloning complete:", output_audio)