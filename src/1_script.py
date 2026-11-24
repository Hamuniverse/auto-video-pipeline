import json
import os
import time
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

load_dotenv()

TOPIC = "Fakta singkat kenapa langit berwarna biru"
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

EXCLUDED_KEYWORDS = (
    "embed", "imagen", "veo", "tts", "audio", "image",
    "aqa", "robotics", "computer", "deep-research", "gemma", "live"
)


def get_candidate_models(client: genai.Client) -> list[str]:
    models = []
    for m in client.models.list():
        name = (m.name or "").replace("models/", "")
        actions = getattr(m, "supported_actions", None) or []
        if "gemini" not in name.lower():
            continue
        if actions and "generateContent" not in actions:
            continue
        if any(k in name.lower() for k in EXCLUDED_KEYWORDS):
            continue
        models.append(name)

    # Prioritaskan varian lite dulu (biasanya lebih longgar), lalu flash, lalu lainnya
    def sort_key(name: str):
        n = name.lower()
        if "lite" in n:
            return (0, n)
        if "flash" in n:
            return (1, n)
        return (2, n)

    return sorted(set(models), key=sort_key)


def generate_script(topic: str) -> dict:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    candidates = get_candidate_models(client)
    if not candidates:
        raise RuntimeError("Tidak ada model Gemini yang tersedia untuk API key ini.")

    print("Model kandidat:", ", ".join(candidates))

    prompt = f"""
    Buat naskah video pendek vertikal (20-30 detik) tentang: "{topic}".
    Kembalikan HANYA JSON valid dengan struktur persis berikut:
    {{
      "title": "Judul menarik maksimal 60 karakter",
      "description": "Deskripsi singkat 2 kalimat beserta 3 hashtag relevan",
      "tags": ["tag1", "tag2", "tag3"],
      "narration": "Teks narasi murni 45-60 kata, bahasa natural, tanpa emoji, tanpa tanda kurung atau arahan visual."
    }}
    """

    last_error = None
    for model_name in candidates:
        for attempt in range(1, 3):  # maksimal 2x coba per model agar cepat pindah
            try:
                print(f"Mencoba {model_name} ({attempt}/2)...")
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    ),
                )
                if not response.text:
                    continue
                return json.loads(response.text)
            except errors.APIError as e:
                last_error = e
                if e.code in (429, 500, 503):
                    print(f"  -> {model_name} sibuk/limit ({e.code}).")
                    if attempt == 1:
                        time.sleep(3)
                else:
                    print(f"  -> {model_name} dilewati ({e.code}).")
                    break

    raise RuntimeError(f"Semua model gagal diakses. Error terakhir: {last_error}")


if __name__ == "__main__":
    data = generate_script(TOPIC)
    (OUTPUT_DIR / "meta.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (OUTPUT_DIR / "narration.txt").write_text(
        data["narration"], encoding="utf-8"
    )
    print("Selesai! Judul:", data["title"])
