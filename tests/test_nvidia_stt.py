"""
Tests ALL supported languages for parakeet-1.1b-rnnt-multilingual-asr
on NVIDIA NVCF hosted endpoint in streaming mode.

Supported languages from NVIDIA docs:
https://docs.nvidia.com/nim/riva/asr/latest/support-matrix.html

Usage: NVIDIA_API_KEY=your_key python test_nvidia_asr_all_languages.py
"""

import os

import riva.client
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("NVIDIA_API_KEY", "your_api_key_here")
FUNCTION_ID = "71203149-d3b7-4460-8231-1be2543a1fca"
SERVER = "grpc.nvcf.nvidia.com:443"
SAMPLE_RATE = 16000

# All languages listed in NVIDIA support matrix for parakeet-1.1b-rnnt-multilingual
LANGUAGES = [
    ("en-US", "English US"),
    ("en-GB", "English GB"),
    ("fr-FR", "French"),
    ("fr-CA", "French Canadian"),
    ("es-ES", "Spanish Spain"),
    ("es-US", "Spanish US"),
    ("de-DE", "German"),
    ("it-IT", "Italian"),
    ("pt-BR", "Portuguese Brazil"),
    ("pt-PT", "Portuguese Portugal"),
    ("ar-AR", "Arabic"),
    ("hi-IN", "Hindi"),
    ("ja-JP", "Japanese"),
    ("ko-KR", "Korean"),
    ("ru-RU", "Russian"),
    ("he-IL", "Hebrew"),
    ("nl-NL", "Dutch"),
    ("nb-NO", "Norwegian Bokmål"),
    ("nn-NO", "Norwegian Nynorsk"),
    ("cs-CZ", "Czech"),
    ("da-DK", "Danish"),
    ("pl-PL", "Polish"),
    ("sv-SE", "Swedish"),
    ("th-TH", "Thai"),
    ("tr-TR", "Turkish"),
    ("multi", "Auto-detect"),
]


def test_language(code: str, name: str):
    metadata = [
        ["function-id", FUNCTION_ID],
        ["authorization", f"Bearer {API_KEY}"],
    ]
    auth = riva.client.Auth(None, True, SERVER, metadata)
    asr_service = riva.client.ASRService(auth)

    config = riva.client.StreamingRecognitionConfig(
        config=riva.client.RecognitionConfig(
            encoding=riva.client.AudioEncoding.LINEAR_PCM,
            language_code=code,
            max_alternatives=1,
            enable_automatic_punctuation=True,
            sample_rate_hertz=SAMPLE_RATE,
            audio_channel_count=1,
        ),
        interim_results=True,
    )

    def fake_audio():
        yield b"\x00" * 3200  # 100ms of silence

    try:
        responses = asr_service.streaming_response_generator(
            audio_chunks=fake_audio(),
            streaming_config=config,
        )
        for response in responses:
            break
        return True, None
    except Exception as e:
        # Extract just the details line
        details = (
            str(e).split("details =")[1].split("\n")[0].strip()
            if "details =" in str(e)
            else str(e)
        )
        return False, details


if __name__ == "__main__":
    passed = []
    failed = []

    print(f"\nTesting {len(LANGUAGES)} languages on NVCF endpoint: {FUNCTION_ID}\n")
    print(f"{'Code':<12} {'Language':<25} {'Result'}")
    print("-" * 70)

    for code, name in LANGUAGES:
        ok, err = test_language(code, name)
        status = "✅ PASS" if ok else "❌ FAIL"
        print(f"{code:<12} {name:<25} {status}")
        if ok:
            passed.append(code)
        else:
            failed.append((code, name, err))

    print("\n" + "=" * 70)
    print(f"✅ PASSED ({len(passed)}): {', '.join(passed)}")
    print(f"\n❌ FAILED ({len(failed)}):")
    for code, name, err in failed:
        print(f"  {code} ({name}): {err}")
