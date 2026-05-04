from app.extract import extract_embedding
from app.generate import generate_speech
from app.convert import convert_voice
from resemblyzer import VoiceEncoder, preprocess_wav
from scipy.spatial.distance import cosine

INPUT_AUDIO = "data/input/my_voice.wav"

TEXT = "Hello, this is a test of my cloned voice."

def evaluate(real_path, fake_path):
    encoder = VoiceEncoder()

    real = encoder.embed_utterance(preprocess_wav(real_path))
    fake = encoder.embed_utterance(preprocess_wav(fake_path))

    similarity = 1 - cosine(real, fake)
    return similarity


def main():
    print("Step 1: Extracting speaker embedding...")
    embedding = extract_embedding(INPUT_AUDIO)

    print("Step 2: Generating base speech...")
    base_audio = generate_speech(TEXT)

    print("Step 3: Converting to cloned voice...")
    cloned_audio = convert_voice(base_audio, embedding)

    print("Step 4: Evaluating similarity...")
    score = evaluate(INPUT_AUDIO, cloned_audio)

    print(f"Voice similarity score: {score:.4f}")


if __name__ == "__main__":
    main()