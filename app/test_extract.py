from openvoice import se_extractor
from openvoice.api import ToneColorConverter

audio_path = "data/input/my_voice.wav"

# ✅ create dummy converter (needed for embedding)
converter = ToneColorConverter(
    config_path="checkpoints_v2/converter/config.json",
    device="cpu"   # or "mps" if you want
)

print("Starting extraction...")

embedding, name = se_extractor.get_se(
    audio_path,
    vc_model=converter,   # ✅ correct argument
    target_dir="data/processed",
    vad=False             # ✅ keep this
)

print("Embedding type:", type(embedding))
print("Audio name:", name)
print("✅ Embedding extracted")