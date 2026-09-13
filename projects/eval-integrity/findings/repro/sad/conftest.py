"""Shared fixtures for the SAD reproductions.

Network to api.github.com is blocked in the audit sandbox, so the fixture stages the
reference clone's structs.zip files (sad_official/, commit dfc5c98) into a temporary
cache directory laid out exactly as inspect_evals.sad.download_data expects.
inspect_ai.util.download() skips the fetch when the file exists with the pinned
sha256, so the port's real loader/unzipper runs unmodified.
"""

import shutil
import subprocess
from pathlib import Path
from typing import Callable
from unittest.mock import patch

import pytest

HERE = Path(__file__).resolve().parent
AUDIT = HERE.parents[2]  # findings/repro/sad -> audit
SAD_OFFICIAL = AUDIT / "sad_official"
EVALUGATOR = AUDIT.parent / "evalugator_official"  # scratchpad clone of LRudL/evalugator


@pytest.fixture(scope="session")
def sad_cache(tmp_path_factory) -> Path:
    from inspect_evals.sad import download_data as dd

    cache = tmp_path_factory.mktemp("sad_cache")
    for zip_path in dd.ZIP_PATHS.values():
        src = SAD_OFFICIAL / "sad" / zip_path / dd.ZIP_FILE_NAME
        dst = cache / zip_path / dd.ZIP_FILE_NAME
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
    with patch("inspect_evals.sad.download_data.CACHE_DIR", cache):
        yield cache


@pytest.fixture(scope="session")
def official_parser() -> Callable[[str, int], int | None]:
    """Return evalugator's MCQ answer parser, loaded verbatim from the reference library.

    `evalugator/__init__.py` imports provider SDKs (openai, ...) that are not installed
    here, so we exec the pure-python parsing helpers from `rendering_utils.py` instead
    of importing the package. The returned callable reproduces
    `parsing.mcquestion_scoring_judgement` for SAD's templates (text answers are NOT
    accepted because "__text__" is not in `answer_styles_accepted`).
    """
    if not EVALUGATOR.exists():
        subprocess.run(
            ["git", "clone", "-q", "https://github.com/LRudL/evalugator.git", str(EVALUGATOR)],
            check=True,
        )
    src = (EVALUGATOR / "evalugator" / "rendering_utils.py").read_text()
    body = src[src.index("def first_letter_that") :]
    from typing import List, Optional, Union, cast

    ns: dict = {
        "List": List,
        "Union": Union,
        "cast": cast,
        "Optional": Optional,
        "MCQRenderInfo": object,
        "Message": object,
        "messages_to_str": None,
    }
    exec(compile(body, str(EVALUGATOR / "evalugator" / "rendering_utils.py"), "exec"), ns)
    mc_format_to_int = ns["mc_format_to_int"]
    styles = ["(A)", "A)", "A"]  # sad/templates.py mcq_with_you_specifier / mcq_with_system

    def parse(output: str, num_choices: int) -> int | None:
        # evalugator.parsing.mcquestion_scoring_judgement: output = response.txt (no strip),
        # ans_i = mc_format_to_int(output, input_styles=..., maximum=num_answers)
        return mc_format_to_int(output, input_styles=styles, maximum=num_choices)

    return parse
