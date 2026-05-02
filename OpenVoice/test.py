import torch
from openvoice import se_extractor
from openvoice.api import ToneColorConverter

import os
from dotenv import load_dotenv
import random
import shutil

load_dotenv()

PATH_TO_VOICE_DATA: str = os.getenv("PATH_TO_VOICE_DATA")
PATH_TO_TRANSCRIPT: str = os.getenv("PATH_TO_TRANSCRIPT")

converter = ToneColorConverter("checkpoints_v2/converter/config.json", device="cpu")
converter.load_ckpt("checkpoints_v2/converter/checkpoint.pth")

def play_audio(path):
    os.system(f"afplay '{path}'")


def get_random_sample():
    full_path = transcript = None
    with open(PATH_TO_TRANSCRIPT, "r", encoding="utf-8") as transcipt_file:
        contents = transcipt_file.readlines()
        chosen_one = random.choice(contents)
        splitted = chosen_one.split("|")
        file_name = splitted[0]
        transcript = splitted[1]

        full_path = os.path.join(PATH_TO_VOICE_DATA, file_name)

    if full_path.startswith("file://"):
        full_path.replace("file://", "")

    return {"path": full_path, "transcript": transcript}


def test(test_n: int):
    print(f"\n{test_n}th TEST START")

    sample = get_random_sample()
    print("Sample selected")
    print("Transcript:", sample["transcript"])
    print("Sample audio play:", sample["path"])
    play_audio(sample["path"])

    output_folder_path = os.path.join(os.getcwd(), "output", f"test_{test_n}")
    os.makedirs(output_folder_path, exist_ok=True)

    target_se, _ = se_extractor.get_se(sample["path"], converter, vad=False)

    selected_line = None
    with open("./source/src.txt", "r", encoding="utf-8") as src:
        lines = src.readlines()
        selected_line = random.choice(lines)
    
    input_path, input_transcript = selected_line.split("|")
    input_path = input_path.strip()

    print("Src selected")
    print("Src transcript:", input_transcript.strip())
    print("Src audio play:", input_path)
    play_audio(input_path)

    source_se, _ = se_extractor.get_se(input_path, converter, vad=False)

    target_save_path = os.path.join(output_folder_path, "target.wav")
    input_save_path = os.path.join(output_folder_path, "input.wav")
    output_save_path = os.path.join(output_folder_path, "output.wav")

    shutil.copy2(sample["path"], target_save_path)
    shutil.copy2(input_path, input_save_path)

    converter.convert(
        audio_src_path=input_path,
        src_se=source_se,
        tgt_se=target_se,
        output_path=output_save_path,
    )

    print(f"Results saved in: {output_folder_path}")
    print(f"{test_n}th TEST END")


if __name__ == "__main__":
    test(1)
