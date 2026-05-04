from openvoice import tone_color_converter
from app.utils import get_device
import soundfile as sf

device = get_device()

def convert_voice(source_audio_path, speaker_embedding, output_path="data/output/cloned.wav"):
    converter = tone_color_converter.ToneColorConverter(device=device)

    converted_audio = converter.convert(
        audio_src_path=source_audio_path,
        src_se=None,
        tgt_se=speaker_embedding
    )

    sf.write(output_path, converted_audio, 22050)

    return output_path