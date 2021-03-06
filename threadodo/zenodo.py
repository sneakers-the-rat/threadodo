import requests
from pathlib import Path
from threadodo.creds import Zenodo_Creds
from threadodo.thread import Thread
import json
from pprint import pprint
from dataclasses import dataclass
import typing
from typing import List
from logging import getLogger

@dataclass
class Deposition:
    doi: str
    doi_url: str
    title: str
    id: str



def post_pdf(pdf:Path,
             thread:Thread,
             creds:Zenodo_Creds=Zenodo_Creds.from_json(Path('zenodo_creds.json')),
             loglevel:str="DEBUG"
             ) -> Deposition:
    """
    https://developers.zenodo.org/#quickstart-upload
    """
    logger = getLogger('threadodo.zenodo')
    logger.setLevel(loglevel)

    params = {'access_token': creds.access_token}
    headers = {"Content-Type": "application/json"}


    dep_r = requests.post('https://zenodo.org/api/deposit/depositions',
                      params=params,
                      headers=headers,
                      data="{}"
                      )
    deposit = dep_r.json()
    logger.info(f'deposition: {dep_r.status_code}')
    logger.debug(deposit)

    with open(pdf, 'rb') as pdf:
        r = requests.put(
            f"{deposit['links']['bucket']}/{pdf.name}",
            data=pdf,
            params=params
        )
    logger.info(f'upload: {r.status_code}')

    metadata = {
        'metadata': {
            'title': thread.title,
            'upload_type': 'publication',
            'publication_type': 'preprint',
            'description': thread.title,
            'creators': [{'name':thread.author.username}]
        }
    }
    meta_r = requests.put(f'https://zenodo.org/api/deposit/depositions/{deposit["id"]}',
                          params=params,
                          data=json.dumps(metadata),
                          headers=headers)
    logger.info(f'meta: {meta_r.status_code}')

    pub_r = requests.post(f'https://zenodo.org/api/deposit/depositions/{deposit["id"]}/actions/publish',
                          params=params)
    logger.info(f'pub: {pub_r.status_code}')
    pub_json = pub_r.json()
    logger.debug(pub_json)
    return Deposition(pub_json['doi'], pub_json['doi_url'], pub_json['title'], pub_json['id'])