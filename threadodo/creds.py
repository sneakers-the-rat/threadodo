"""
No, not the actual creds. and dont go lookin for em in the git history cuz they aint in there neither
"""

import json
from dataclasses import dataclass
from pathlib import Path
import typing

@dataclass
class Creds:
    api_key: str
    api_secret: str
    bearer_token: str
    access_token: typing.Optional[str]
    access_secret: typing.Optional[str]

    @classmethod
    def from_json(cls, path:Path) -> 'Creds':
        with open(path, 'r') as jfile:
            creds = json.load(jfile)
        return Creds(**creds)


@dataclass
class Zenodo_Creds:
    access_token:str

    @classmethod
    def from_json(cls, path:Path) -> 'Zenodo_Creds':
        with open(path, 'r') as jfile:
            creds = json.load(jfile)
        return Zenodo_Creds(**creds)