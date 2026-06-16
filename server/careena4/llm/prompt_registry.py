from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


PROMPT_DIR = Path(__file__).resolve().parent / "prompts"


@dataclass(frozen=True)
class PromptTemplate:
    name: str
    version: str
    system_prompt: str


@lru_cache(maxsize=None)
def load_prompt(name: str) -> PromptTemplate:
    path = PROMPT_DIR / f"{name}.md"
    raw_text = path.read_text(encoding="utf-8").strip()
    version, system_prompt = _parse_prompt_file(raw_text)
    return PromptTemplate(name=name, version=version, system_prompt=system_prompt)


def _parse_prompt_file(raw_text: str) -> tuple[str, str]:
    lines = raw_text.splitlines()
    if not lines:
        raise ValueError("Prompt file is empty")

    first_line = lines[0].strip()
    if not first_line.lower().startswith("version:"):
        raise ValueError("Prompt file must start with 'version:'")

    version = first_line.split(":", 1)[1].strip()
    body_lines = lines[1:]
    if body_lines and body_lines[0].strip() == "---":
        body_lines = body_lines[1:]

    system_prompt = "\n".join(body_lines).strip()
    if not system_prompt:
        raise ValueError("Prompt file body is empty")
    return version, system_prompt
