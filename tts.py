from pathlib import Path
import pandas as pd
from gtts import gTTS
from pydub import AudioSegment


def fix_german(word: str) -> str:
    # add article
    if not word or len(word) < 2:
        return word

    if word.startswith("e "):  # die
        return f"die {word[2:]}"
    elif word.startswith("s "):  # das
        return f"das {word[2:]}"
    elif word.startswith("r "):  # der
        return f"der {word[2:]}"
    else:
        print(f"German article not found in {word}")
        return word


def fix_english(word: str) -> str:
    # add article
    if not word:
        return word
    if word in [
        "yellow",
    ]:
        return word
    if word.startswith("to "):
        print(f"English article not found in {word}")
        return word
    if word.startswith("a "):
        print(f"English article not found in {word}")
        return word
    if word.startswith("in "):
        print(f"English article not found in {word}")
        return word
    if word[0].isupper():
        print(f"English article not found in {word}")
        return word
    if "!" in word:
        print(f"English article not found in {word}")
        return word
    return f"the {word}"


def generate_tts(
        df: pd.DataFrame,
        prefix: str = "",
        overwrite: bool = False,
        pause_duration_ms: int = 1000,
):
    print("\n")

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

    root_saving_dir = Path("tts_output")
    saving_dir = root_saving_dir / prefix
    saving_dir.mkdir(exist_ok=True, parents=True)

    pause = AudioSegment.silent(duration=pause_duration_ms)

    # -------------------------------

    all_files = []

    for i, row in df.iterrows():
        idx = row['#']
        # assert i == idx, f"index mismatch : {i} != {idx}"

        row_name = row['English'].replace(' ', '_').replace('/', '_')

        saving_path = saving_dir / f"{row_name}.mp3"

        all_files.append(saving_path)

        if saving_path.exists() and (not overwrite):
            print(f"❌ already exists : {saving_path}")
            continue

        # -------------------------------

        audio_segments = []

        for lang in lang_map.keys():
            text = row[lang]
            lang_code = lang_map[lang]

            temp_file = saving_dir / f"tmp_{lang}.mp3"
            gTTS(text=text, lang=lang_code).save(str(temp_file))

            segment = AudioSegment.from_mp3(str(temp_file))
            audio_segments.append(segment + pause)

        # concatenate 5 languages
        combined = sum(audio_segments)
        combined.export(str(saving_path), format="mp3")

        print(f"✅ generated [{idx}/{len(df)}] : {saving_path}")


    # -------------------------------
    # clean up
    for lang in lang_map.keys():
        temp_file = saving_dir / f"tmp_{lang}.mp3"
        if temp_file.exists():
            print(f"❌ removing : {temp_file}")
            temp_file.unlink()

    # -------------------------------
    # concatenate all
    name_saved = set([p.stem for p in saving_dir.glob("*.mp3")])
    name_required = set([p.stem for p in all_files])
    print(f"missing   : {name_required - name_saved}")
    print(f"not needed: {name_saved - name_required}")

    final_audio = AudioSegment.empty()
    for file in all_files:
        final_audio += pause + AudioSegment.from_mp3(file)
    final_audio += pause

    saving_path = root_saving_dir / f"{prefix}__{len(all_files)}_rows.mp3"
    # if not saving_path.exists() and overwrite:
    final_audio.export(saving_path, format="mp3")
    print(f"🎉 final generated : {saving_path}")
