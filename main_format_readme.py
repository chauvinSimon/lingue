import pandas as pd
from pathlib import Path

from utils import read_file, save_file, yaml_load

readme_template_path = Path("README_template.md")
readme_path = Path("README.md")

five_lang_path = Path("five_lang.yaml")
five_lang_path_second_rank = Path("five_lang_second_rank.yaml")


# sort alphabetically
def key_without_article(s):
    articles = ["les ", "la ", "le ", "l'"]
    for article in articles:
        if s.startswith(article):
            return s[len(article):]
    raise ValueError(f"Article not found in {s}")


def add_five_lang(content: str) -> str:
    for file_path, content_placeholder in zip(
            [five_lang_path, five_lang_path_second_rank],
            ["\nCONTENT_FIVE_LANG\n", "\nCONTENT_FIVE_LANG_SECOND_RANK\n"]
    ):
        df = pd.DataFrame(
            yaml_load(file_path=file_path),
            columns=["French", "Italian", "German", "English", "Spanish", "Notes"]
        )

        df = df.sort_values(by="French", key=lambda col: col.map(key_without_article))

        table = df.to_markdown(
            index=False,
            colalign=["center"] * len(df.columns)
        )

        content = content.replace(content_placeholder, f"\n{table}\n")

    return content


def main() -> None:
    content = read_file(file_path=readme_template_path)
    content = add_five_lang(content)
    save_file(file_path=readme_path, content=content)


if __name__ == '__main__':
    main()
