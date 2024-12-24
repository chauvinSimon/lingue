import pandas as pd
from pathlib import Path

from utils import read_file, save_file, yaml_load

readme_template_path = Path("README_template.md")
readme_path = Path("README.md")

fra_masc_path = Path("fra_masc_ita_fem.yaml")
fra_fem_path = Path("fra_fem_ita_masc.yaml")
five_lang_path = Path("five_lang.yaml")


def add_fra_it(content: str) -> str:
    for suffix, file_path, content_placeholder in zip(
            ["masc", "fem"],
            [fra_masc_path, fra_fem_path],
            ["\nCONTENT_FRA_MASC\n", "\nCONTENT_FRA_FEM\n"]
    ):
        df = pd.DataFrame(
            yaml_load(file_path=file_path),
            columns=["French", "Italian", "Notes"]
        )

        table = df.to_markdown(
            index=False,
            colalign=["center"] * len(df.columns)

        )

        content = content.replace(content_placeholder, f"\n{table}\n")

    return content


def add_five_lang(content: str) -> str:
    content_placeholder = "\nCONTENT_FIVE_LANG\n"
    df = pd.DataFrame(
        yaml_load(file_path=five_lang_path),
        columns=["French", "Italian", "German", "English", "Spanish", "Notes"]
    )

    table = df.to_markdown(
        index=False,
        colalign=["center"] * len(df.columns)

    )

    return content.replace(content_placeholder, f"\n{table}\n")


def main() -> None:
    content = read_file(file_path=readme_template_path)
    content = add_fra_it(content)
    content = add_five_lang(content)
    save_file(file_path=readme_path, content=content)

if __name__ == '__main__':
    main()