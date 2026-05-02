#!/usr/bin/env python3
"""Clone a reference voice with OpenVoice V2 and generate multilingual speech.

This script wraps the official OpenVoice V2 demo flow:
1. Generate base speech with MeloTTS.
2. Extract a target speaker embedding from a reference audio file.
3. Convert each base speech file to the target tone color with OpenVoice.

The script can also install local editable packages and download the official
OpenVoice V2 checkpoints.
"""

from __future__ import annotations

import argparse
import re
import json
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path
from typing import Dict, Iterable, Optional, Tuple


OPENVOICE_V2_URL = (
    "https://myshell-public-repo-host.s3.amazonaws.com/"
    "openvoice/checkpoints_v2_0417.zip"
)

LANGUAGES: Dict[str, Dict[str, str]] = {
    "en": {
        "melo": "EN_NEWEST",
        "name": "English",
        "sample": "Hello, this is a test.",
    },
    "es": {
        "melo": "ES",
        "name": "Spanish",
        "sample": "Hola, esto es una prueba.",
    },
    "fr": {
        "melo": "FR",
        "name": "French",
        "sample": "Bonjour, ceci est un test.",
    },
    "zh": {
        "melo": "ZH",
        "name": "Chinese",
        "sample": "你好，这是一个测试。",
    },
    "jp": {
        "melo": "JP",
        "name": "Japanese",
        "sample": "こんにちは、これはテストです。",
    },
    "kr": {
        "melo": "KR",
        "name": "Korean",
        "sample": "안녕하세요, 이것은 테스트입니다.",
    },
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def run(cmd: Iterable[str], cwd: Optional[Path] = None) -> None:
    printable = " ".join(str(part) for part in cmd)
    print(f"Running: {printable}")
    subprocess.run(list(cmd), cwd=str(cwd) if cwd else None, check=True)


def install_dependencies(root: Path) -> None:
    """Install OpenVoice, MeloTTS, and Japanese dictionary resources."""
    openvoice_dir = root / "OpenVoice"
    melotts_dir = root / "MeloTTS"

    if not openvoice_dir.exists() or not melotts_dir.exists():
        raise FileNotFoundError(
            "Expected local OpenVoice and MeloTTS directories at the repository root."
        )

    run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    run([sys.executable, "-m", "pip", "install", "-e", str(openvoice_dir)])
    run([sys.executable, "-m", "pip", "install", "-e", str(melotts_dir)])
    run([sys.executable, "-m", "unidic", "download"])


def download_file(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url) as response, destination.open("wb") as out_file:
        shutil.copyfileobj(response, out_file)


def download_checkpoints(checkpoints_dir: Path, force: bool = False) -> None:
    """Download and extract official OpenVoice V2 checkpoints."""
    converter_config = checkpoints_dir / "converter" / "config.json"
    converter_ckpt = checkpoints_dir / "converter" / "checkpoint.pth"
    ses_dir = checkpoints_dir / "base_speakers" / "ses"

    if not force and converter_config.exists() and converter_ckpt.exists() and ses_dir.exists():
        print(f"OpenVoice V2 checkpoints already exist: {checkpoints_dir}")
        return

    checkpoints_dir.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="openvoice_v2_") as tmp:
        zip_path = Path(tmp) / "checkpoints_v2_0417.zip"
        extract_dir = Path(tmp) / "extract"
        print(f"Downloading OpenVoice V2 checkpoints from {OPENVOICE_V2_URL}")
        download_file(OPENVOICE_V2_URL, zip_path)

        print("Extracting checkpoints")
        with zipfile.ZipFile(zip_path, "r") as archive:
            archive.extractall(extract_dir)

        extracted = extract_dir / "checkpoints_v2"
        if not extracted.exists():
            candidates = [p for p in extract_dir.iterdir() if p.is_dir()]
            if len(candidates) == 1:
                extracted = candidates[0]
            else:
                raise RuntimeError("Could not locate checkpoints_v2 in downloaded archive.")

        if checkpoints_dir.exists() and force:
            shutil.rmtree(checkpoints_dir)
        shutil.copytree(extracted, checkpoints_dir, dirs_exist_ok=True)

    print(f"OpenVoice V2 checkpoints ready: {checkpoints_dir}")


def add_local_packages_to_path(root: Path) -> None:
    """Allow running from this repo before editable installs are performed."""
    for package_dir in (root / "OpenVoice", root / "MeloTTS"):
        if package_dir.exists():
            sys.path.insert(0, str(package_dir))


def parse_texts(args: argparse.Namespace) -> Dict[str, str]:
    if args.texts_json:
        data = json.loads(Path(args.texts_json).read_text(encoding="utf-8"))
        texts = {key.lower(): str(value) for key, value in data.items()}
    elif args.text:
        texts = {key: args.text for key in LANGUAGES}
    else:
        texts = {key: meta["sample"] for key, meta in LANGUAGES.items()}

    missing = [key for key in args.languages if key not in texts]
    if missing:
        raise ValueError(f"Missing text for language code(s): {', '.join(missing)}")
    return texts


def safe_name(value: str) -> str:
    name = re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("._")
    return name or "reference"


def choose_device(requested: str) -> str:
    import torch

    if requested != "auto":
        if requested.startswith("cuda") and not torch.cuda.is_available():
            raise RuntimeError("CUDA was requested, but torch.cuda.is_available() is False.")
        return requested
    return "cuda:0" if torch.cuda.is_available() else "cpu"


def load_source_embedding(
    ses_dir: Path,
    speaker_key: str,
    language_code: str,
    device: str,
) -> Tuple[object, Path]:
    import torch

    normalized = speaker_key.lower().replace("_", "-")
    candidates = [
        ses_dir / f"{normalized}.pth",
        ses_dir / f"{language_code}.pth",
        ses_dir / f"{language_code.lower()}.pth",
    ]
    candidates.extend(sorted(ses_dir.glob(f"*{normalized}*.pth")))
    candidates.extend(sorted(ses_dir.glob(f"*{language_code.lower()}*.pth")))

    for candidate in candidates:
        if candidate.exists():
            return torch.load(candidate, map_location=device), candidate

    available = ", ".join(path.name for path in sorted(ses_dir.glob("*.pth"))[:25])
    raise FileNotFoundError(
        f"Could not find a source speaker embedding for '{speaker_key}' in {ses_dir}. "
        f"Available examples: {available}"
    )


def generate_multilingual_clones(args: argparse.Namespace) -> None:
    root = repo_root()
    add_local_packages_to_path(root)

    import torch
    from melo.api import TTS
    from openvoice import se_extractor
    from openvoice.api import ToneColorConverter

    device = choose_device(args.device)
    if device == "cpu" and torch.backends.mps.is_available():
        torch.backends.mps.is_available = lambda: False
    checkpoints_dir = Path(args.checkpoints_dir).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    reference_audio = Path(args.reference_audio).expanduser().resolve()
    texts = parse_texts(args)

    if not reference_audio.exists():
        raise FileNotFoundError(f"Reference audio does not exist: {reference_audio}")

    converter_dir = checkpoints_dir / "converter"
    ses_dir = checkpoints_dir / "base_speakers" / "ses"
    if not (converter_dir / "config.json").exists() or not (converter_dir / "checkpoint.pth").exists():
        raise FileNotFoundError(
            f"Missing OpenVoice V2 converter checkpoint in {converter_dir}. "
            "Run this script with --download-checkpoints first."
        )
    if not ses_dir.exists():
        raise FileNotFoundError(f"Missing OpenVoice V2 base speaker embeddings: {ses_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir = output_dir / "_tmp"
    tmp_dir.mkdir(exist_ok=True)

    print(f"Using device: {device}")
    converter = ToneColorConverter(
        str(converter_dir / "config.json"),
        device=device,
        enable_watermark=not args.disable_watermark,
    )
    converter.load_ckpt(str(converter_dir / "checkpoint.pth"))

    print(f"Extracting target speaker embedding from {reference_audio}")
    if args.disable_vad:
        audio_name = safe_name(reference_audio.stem)
        se_path = tmp_dir / "speaker_embeddings" / audio_name / "se.pth"
        target_se = converter.extract_se([str(reference_audio)], se_save_path=str(se_path))
    else:
        target_se, audio_name = se_extractor.get_se(
            str(reference_audio),
            converter,
            target_dir=str(tmp_dir / "speaker_embeddings"),
            vad=True,
        )

    for lang in args.languages:
        meta = LANGUAGES[lang]
        melo_language = meta["melo"]
        text = texts[lang]
        base_audio_path = tmp_dir / f"{lang}_base.wav"
        output_path = output_dir / f"{lang}_{audio_name}_openvoice_v2.wav"

        print(f"Generating {meta['name']} base speech with MeloTTS ({melo_language})")
        model = TTS(language=melo_language, device=device)
        speaker_ids = model.hps.data.spk2id
        if args.speaker and args.speaker in speaker_ids:
            speaker_key = args.speaker
        elif args.speaker and args.speaker not in speaker_ids:
            available = ", ".join(speaker_ids.keys())
            raise ValueError(f"Speaker '{args.speaker}' not found. Available: {available}")
        else:
            speaker_key = next(iter(speaker_ids.keys()))
        speaker_id = speaker_ids[speaker_key]

        source_se, source_se_path = load_source_embedding(
            ses_dir=ses_dir,
            speaker_key=speaker_key,
            language_code=melo_language.lower(),
            device=device,
        )

        print(f"Converting tone color using source embedding {source_se_path.name}")
        model.tts_to_file(text, speaker_id, str(base_audio_path), speed=args.speed, quiet=args.quiet)
        converter.convert(
            audio_src_path=str(base_audio_path),
            src_se=source_se,
            tgt_se=target_se,
            output_path=str(output_path),
            tau=args.tau,
            message=args.watermark_message,
        )
        print(f"Saved: {output_path}")

        del model
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="OpenVoice V2 multilingual voice cloning with MeloTTS base speech."
    )
    parser.add_argument("--reference-audio", help="Path to the target voice sample.")
    parser.add_argument("--text", help="Text to synthesize for every selected language.")
    parser.add_argument(
        "--texts-json",
        help="JSON file mapping en/es/fr/zh/jp/kr to language-specific text.",
    )
    parser.add_argument("--output-dir", default="outputs_openvoice_v2")
    parser.add_argument("--checkpoints-dir", default=str(repo_root() / "OpenVoice" / "checkpoints_v2"))
    parser.add_argument(
        "--languages",
        nargs="+",
        default=["kr"],
        choices=list(LANGUAGES.keys()),
        help="Language codes to generate.",
    )
    parser.add_argument("--device", default="auto", help="auto, cpu, cuda, or cuda:0.")
    parser.add_argument("--speed", type=float, default=1.0)
    parser.add_argument("--tau", type=float, default=0.3, help="OpenVoice conversion strength.")
    parser.add_argument("--speaker", help="Optional MeloTTS speaker key.")
    parser.add_argument("--watermark-message", default="@MyShell")
    parser.add_argument("--disable-watermark", action="store_true")
    parser.add_argument("--disable-vad", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--install-deps", action="store_true")
    parser.add_argument("--download-checkpoints", action="store_true")
    parser.add_argument("--force-download", action="store_true")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    root = repo_root()

    try:
        if args.install_deps:
            install_dependencies(root)
        if args.download_checkpoints:
            download_checkpoints(
                checkpoints_dir=Path(args.checkpoints_dir).expanduser().resolve(),
                force=args.force_download,
            )
        if args.reference_audio:
            generate_multilingual_clones(args)
        elif not args.install_deps and not args.download_checkpoints:
            parser.error("Provide --reference-audio, --install-deps, or --download-checkpoints.")
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
