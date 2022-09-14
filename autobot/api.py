"""Interface to the OpenAI API."""
import hashlib
import json
import logging
import os
from typing import List, Optional, Union

import openai

from autobot.utils import cache


def init() -> None:
    openai.organization = os.environ["OPENAI_ORGANIZATION"]
    openai.api_key = os.environ["OPENAI_API_KEY"]


def create_completion(
    prompt: str,
    max_tokens: int,
    temperature: int = 0,
    model: str = "text-davinci-002",
    stop: Optional[Union[str, List[str]]] = None,
) -> openai.Completion:
    request_hash = hashlib.md5(
        json.dumps(
            {
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "model": model,
                "stop": stop,
            }
        ).encode("utf-8")
    ).hexdigest()

    if response := cache.get_from_cache(request_hash):
        logging.info("Reading response from cache...")
        return response

    response = openai.Completion.create(
        model=model,
        prompt=prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        stop=stop,
    )
    cache.set_in_cache(request_hash, response)
    return response
