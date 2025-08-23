from pathlib import Path
import pandas as pd
from gtts import gTTS
from pydub import AudioSegment


def fix_german(word: str) -> str:
    # add article
    if not word or len(word) < 2:
        return word

    first = word[0].lower()
    rest = word[2:].strip() if word[1] == " " else word[1:].strip()

    if first == "e":  # die
        return f"die {rest}"
    elif first == "s":  # das
        return f"das {rest}"
    elif first == "r":  # der
        return f"der {rest}"
    else:
        return word


def fix_english(word: str) -> str:
    # add article
    if not word:
        return word
    return f"the {word}"


def generate_tts(
        df: pd.DataFrame,
        prefix: str = "",
        overwrite: bool = False,
):
    # df = df[:3]

    df["German"] = df["German"].apply(fix_german)
    df["English"] = df["English"].apply(fix_english)

    # -------------------------------

    lang_map = {
        "French": "fr",
        "Italian": "it",
        "German": "de",
        "English": "en",
        "Spanish": "es"
    }

    saving_dir = Path("tts_output") / prefix
    saving_dir.mkdir(exist_ok=True, parents=True)

    # 1sec break between words
    pause = AudioSegment.silent(duration=1000)

    # -------------------------------

    all_files = []

    for _, row in df.iterrows():
        idx = row['#']

        row_name = row['English'].replace(' ', '_')

        saving_path = saving_dir / f"{row_name}.mp3"

        all_files.append(str(saving_path))

        if saving_path.exists() and (not overwrite):
            print(f"❌ already exists : {saving_path}")
            continue

        # -------------------------------

        audio_segments = []

        for lang in lang_map.keys():
            text = row[lang]
            lang_code = lang_map[lang]

            temp_file = saving_dir / f"tmp_{idx}_{lang}.mp3"
            gTTS(text=text, lang=lang_code).save(str(temp_file))

            segment = AudioSegment.from_mp3(str(temp_file))
            audio_segments.append(segment + pause)

        # concatenate 5 languages
        combined = sum(audio_segments)
        combined.export(str(saving_path), format="mp3")

        print(f"✅ generated : {saving_path}")

    # -------------------------------
    # concatenate all
    final_audio = AudioSegment.empty()

    for file in all_files:
        final_audio += AudioSegment.from_mp3(file) + pause

    saving_path = saving_dir / "all_rows.mp3"
    final_audio.export(saving_path, format="mp3")
    print(f"🎉 final generated : {saving_path}")
