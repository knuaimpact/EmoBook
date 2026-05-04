import os
from openvoice import se_extractor

def extract_embedding(audio_path, output_dir="data/processed"):
    os.makedirs(output_dir, exist_ok=True)

    speaker_embedding = se_extractor.get_se(
        audio_path,
        tone_color_converter=None,
        target_dir=output_dir,
        vad=True
    )

    return speaker_embedding