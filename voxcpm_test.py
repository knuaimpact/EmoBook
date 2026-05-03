from pathlib import Path

from google.colab import files
from IPython.display import Audio, display
import soundfile as sf
from voxcpm import VoxCPM


# uploaded = files.upload()
# reference_audio = list(uploaded.keys())[0]
reference_audio = "sample.mp3"


def next_versioned_output_path(output_path: str | Path) -> str:
    path = Path(output_path)
    version = 1

    while True:
        candidate = path.with_name(f"{path.stem}_v{version}{path.suffix}")
        if not candidate.exists():
            return str(candidate)
        version += 1


model = VoxCPM.from_pretrained(
    "openbmb/VoxCPM2",
    load_denoiser=False,
    optimize=False,
)

story_text = """
옛날 어느 작은 숲속 마을에 별을 좋아하는 토끼가 살고 있었어요.
토끼는 매일 밤 하늘을 바라보며 반짝이는 별들에게 인사를 했습니다.

그런데

하늘에서 별 하나가 떨어졌어요!

"우와!"
토끼는 깜짝 놀랐답니다.
"""

wav = model.generate(
    text=story_text,
    reference_wav_path=reference_audio,
    cfg_value=3.0,  # 감정조절
    inference_timesteps=20,  # 감정조절
)

output_path = next_versioned_output_path("voicecopy_story.wav")
sf.write(output_path, wav, model.tts_model.sample_rate)

display(Audio(output_path))
files.download(output_path)
