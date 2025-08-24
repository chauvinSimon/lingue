import pandas as pd
from pathlib import Path

from tts import generate_tts, merge_audio_files
from utils import read_file, save_file, yaml_load

readme_template_path = Path("README_template.md")
readme_path = Path("README.md")

five_lang_path = Path("five_lang.yaml")

url_text = "_Listen to the pronunciation (open this link in a new tab)_"

mp3_urls = {
    1: "https://drive.google.com/file/d/1bLlh6BvSxVieti2Jphqm5I3xWusp8lEt/view?usp=sharing",
    2: "https://drive.google.com/file/d/107E3Uvfrimk_DphrhZs2OLFLumYZIdM-/view?usp=sharing",
    3: "https://drive.google.com/file/d/10xHgtNsL4ZsGMPndqQbh5G0sxbUz0GfH/view?usp=sharing",
}

# sort alphabetically
def key_without_article(s):
    articles = ["les ", "la ", "le ", "l'"]
    for article in articles:
        if s.startswith(article):
            return s[len(article):].lower()
    print(f"Article not found in {s}")
    return s.lower()

def add_five_lang(content: str) -> str:
    df = pd.DataFrame(
        yaml_load(file_path=five_lang_path),
        columns=["category", "French", "Italian", "German", "English", "Spanish", " :wink: "]
    )

    # detect duplicates
    df_lower = df.apply(lambda x: x.str.lower() if x.dtype == "object" else x)
    for column_to_check in ["French", "Italian", "German", "English", "Spanish"]:
        dup = df_lower[df_lower.duplicated([column_to_check], keep=False)]
        if not dup.empty:
            print(f"duplicate in {column_to_check}:\n{dup}")

    for category, content_placeholder in zip(
            [1, 2, 3],
            ["\nCONTENT_FIVE_LANG\n", "\nCONTENT_FIVE_LANG_SECOND_RANK\n", "\nCONTENT_FIVE_LANG_THIRD_RANK\n"]
    ):
        _df = df[df["category"] == category]
        _df = _df.sort_values(by="French", key=lambda col: col.map(key_without_article))

        _df = _df.drop(columns=["category"])

        _df.insert(0, "#", range(1, len(_df) + 1))

        generate_tts(_df, prefix=f"{category}")

        _df.rename(columns={
            'French': 'French ( :fr: )',
            'Italian': 'Italian ( :it: )',
            'German': 'German ( :de: )',
            'English': 'English ( :uk: )',
            'Spanish': 'Spanish ( :es: )'
        }, inplace=True)

        table = _df.to_markdown(
            index=False,
            colalign=["center"] * len(_df.columns)
        )

        url_link = f":arrow_forward: [ {url_text} ]({mp3_urls[category]}) :speaking_head: :loud_sound:"
        content = content.replace(content_placeholder, f"\n{url_link}\n\n{table}\n")
    return content


def main() -> None:
    content = read_file(file_path=readme_template_path)
    content = add_five_lang(content)
    save_file(file_path=readme_path, content=content)

    # create mp3 from all mp3 present in the same directory
    merge_audio_files()


if __name__ == '__main__':
    main()
