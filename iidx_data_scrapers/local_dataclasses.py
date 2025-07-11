import logging
from enum import Enum
from concurrent.futures import Future
from dataclasses import dataclass, field
from typing import Optional

# from numpy.typing import NDArray  # type: ignore

log = logging.getLogger(__name__)

"""
This is a kitchen sink of utility classes for
parsing and maintaining data across several of 
the projects on this repo.

This should eventually be refactored into a
self-standing module that the other scripts can 
import (to also ensure that we aren't vendoring old versions), 
but that's future me's problem.
"""


class TitleType(Enum):
    NORMAL = "NORMAL"
    INFINITAS = "INFINITAS"
    LEGGENDARIA = "LEGGENDARIA"


class Difficulty(Enum):
    SP_NORMAL = 2
    SP_HYPER = 3
    SP_ANOTHER = 4
    SP_LEGGENDARIA = 5
    DP_NORMAL = 7
    DP_HYPER = 8
    DP_ANOTHER = 9
    DP_LEGGENDARIA = 10
    UNKNOWN = 99


class DifficultyType(Enum):
    NORMAL = 0
    HYPER = 1
    ANOTHER = 2
    LEGGENDARIA = 3
    UNKNOWN = 99


class SingleOrDouble(Enum):
    SP = 2
    DP = 7


class Alphanumeric(Enum):
    ABCD = 0
    EFGH = 1
    IJKL = 2
    MNOP = 3
    QRST = 4
    UVWXYZ = 5
    OTHERS = 6


class ClearType(Enum):
    FAILED = 0
    ASSIST = 1
    EASY = 2
    NORMAL = 3
    HARD = 4
    EXHARD = 5
    FULL_COMBO = 6
    NO_PLAY = 7
    UNKNOWN = 99


@dataclass
class DifficultyMetadata:
    level: int = 0
    notes: int = 0
    min_bpm: int = 0
    max_bpm: int = 0
    soflan: bool = False


def generate_difficulty_metadata() -> dict[Difficulty, DifficultyMetadata]:
    return {
        Difficulty.SP_NORMAL: DifficultyMetadata(),
        Difficulty.SP_HYPER: DifficultyMetadata(),
        Difficulty.SP_ANOTHER: DifficultyMetadata(),
        Difficulty.SP_LEGGENDARIA: DifficultyMetadata(),
        Difficulty.DP_NORMAL: DifficultyMetadata(),
        Difficulty.DP_HYPER: DifficultyMetadata(),
        Difficulty.DP_ANOTHER: DifficultyMetadata(),
        Difficulty.DP_LEGGENDARIA: DifficultyMetadata(),
    }


@dataclass
class SongMetadata:
    textage_id: str
    title: str
    artist: str
    genre: str
    textage_version_id: int
    alphanumeric: Alphanumeric
    difficulty_metadata: dict[Difficulty, DifficultyMetadata] = field(
        default_factory=generate_difficulty_metadata
    )
    version: str = ""

    def to_dict(self) -> dict:
        return {
            "textage_id": self.textage_id,
            "title": self.title,
            "artist": self.artist,
            "genre": self.genre,
            "textage_version_id": self.version,
            "version": self.version,
            "alphanumeric": self.alphanumeric.name,
            "difficulty_metadata": {
                difficulty.name: {
                    "level": self.difficulty_metadata[difficulty].level,
                    "notes": self.difficulty_metadata[difficulty].notes,
                    "soflan": self.difficulty_metadata[difficulty].soflan,
                    "min_bpm": self.difficulty_metadata[difficulty].min_bpm,
                    "max_bpm": self.difficulty_metadata[difficulty].max_bpm,
                }
                for difficulty in self.difficulty_metadata.keys()
                if self.difficulty_metadata[difficulty].notes != 0
                and self.difficulty_metadata[difficulty].level != 0
            },
        }

    def sort_by_alphanumeric(self) -> str:
        """
        Primary sorting method, also used as the secondary
        sorting method when generating the static site.
        """
        return f"{self.alphanumeric.value} {self.title}"

    def sort_by_version(self) -> str:
        """
        Return formatted version strings, then alphabetically.
        subtream has a special case in textage data we work around,
        by setting it to the last element of the version list,
        and then reformatting strings so it comes alphabetically
        between 1 and 2. (that's what all the 0 padding is for
        in the return string)
        """
        unchecked_version_id: int = self.textage_version_id
        checked_version_id: float = 0.0
        # substream textage workaround
        if unchecked_version_id == -1:
            checked_version_id = 1.5
        else:
            checked_version_id = float(unchecked_version_id)
        return f"{checked_version_id:04.1f} {self.sort_by_alphanumeric()}"

    def __check_difficulty_rate(self, difficulty: Difficulty) -> str:
        """
        set any blanks to appear after other entries by setting them to ZZZ.
        Otherwise prepend 0s to any single digit difficulties for string
        based sorting.
        """
        if (
            difficulty not in self.difficulty_metadata
            or self.difficulty_metadata[difficulty].level == 0
        ):
            return "ZZZ"
        return f"{self.difficulty_metadata[difficulty].level:02d}"

    def sort_by_spn(self) -> str:
        rate = self.__check_difficulty_rate(Difficulty.SP_NORMAL)
        return f"{rate} " + self.sort_by_alphanumeric()

    def sort_by_sph(self) -> str:
        rate = self.__check_difficulty_rate(Difficulty.SP_HYPER)
        return f"{rate} " + self.sort_by_alphanumeric()

    def sort_by_spa(self) -> str:
        rate = self.__check_difficulty_rate(Difficulty.SP_ANOTHER)
        return f"{rate} " + self.sort_by_alphanumeric()

    def sort_by_spl(self) -> str:
        rate = self.__check_difficulty_rate(Difficulty.SP_LEGGENDARIA)
        return f"{rate} " + self.sort_by_alphanumeric()

    def sort_by_dpn(self) -> str:
        rate = self.__check_difficulty_rate(Difficulty.DP_NORMAL)
        return f"{rate} " + self.sort_by_alphanumeric()

    def sort_by_dph(self) -> str:
        rate = self.__check_difficulty_rate(Difficulty.DP_HYPER)
        return f"{rate} " + self.sort_by_alphanumeric()

    def sort_by_dpa(self) -> str:
        rate = self.__check_difficulty_rate(Difficulty.DP_ANOTHER)
        return f"{rate} " + self.sort_by_alphanumeric()

    def sort_by_dpl(self) -> str:
        rate = self.__check_difficulty_rate(Difficulty.DP_LEGGENDARIA)
        return f"{rate} " + self.sort_by_alphanumeric()
