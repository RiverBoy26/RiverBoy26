#!/usr/bin/env python3
"""Translate visible text in a lowlighter/metrics isocalendar SVG.

Does not modify shapes, CSS, or SVG element attributes. Needs only Python 3.
Usage: python3 scripts/translate_metrics.py metrics.plugin.isocalendar.svg
"""

from pathlib import Path
import re
import sys

# Longer phrases first so that fragments do not interfere with replacements.
TRANSLATIONS = (
    (r"Contributions calendar", "Календарь активности"),
    (r"Commits streaks", "Серии коммитов"),
    (r"Commits per day", "Коммиты за день"),
    (r"Current streak", "Текущая серия"),
    (r"Best streak", "Лучшая серия"),
    (r"Highest in a day at", "Максимум за день:"),
    (r"Average per day at", "Среднее за день:"),
    (r"\bdays\b", "дней"),
    (r"\bday\b", "день"),
)

# Match plain text between XML tags; do not touch SVG markup or attributes.
TEXT_NODE = re.compile(r"(?<=>)([^<>]+)(?=<)")


def translate_text(text: str) -> str:
    for pattern, replacement in TRANSLATIONS:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    # Natural endings of Russian plurals for generated streak counters.
    text = re.sub(
        r"(Текущая серия|Лучшая серия)(\s*:?[\s]*)(\d+)\s+дней",
        lambda m: f"{m[1]}{m[2]}{m[3]} {day_word(int(m[3]))}",
        text,
    )
    return text


def day_word(number: int) -> str:
    if number % 10 == 1 and number % 100 != 11:
        return "день"
    if 2 <= number % 10 <= 4 and not 12 <= number % 100 <= 14:
        return "дня"
    return "дней"


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: translate_metrics.py PATH_TO_SVG")

    path = Path(sys.argv[1])
    svg = path.read_text(encoding="utf-8")
    if "<svg" not in svg:
        raise SystemExit(f"Not an SVG document: {path}")

    translated = TEXT_NODE.sub(lambda match: translate_text(match[1]), svg)
    if translated == svg:
        print("Warning: no matching labels found; check current metrics SVG format")
    path.write_text(translated, encoding="utf-8")
    print(f"Translated SVG: {path}")


if __name__ == "__main__":
    main()
