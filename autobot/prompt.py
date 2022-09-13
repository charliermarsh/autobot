from typing import List, NamedTuple, Optional, Union, cast

from autobot import api
from autobot.transforms import TransformType


class Prompt(NamedTuple):
    text: str
    max_tokens: int
    stop: Optional[Union[str, List[str]]]


def make_prompt(
    snippet: str,
    *,
    transform_type: TransformType,
    before_text: str,
    after_text: str,
    before_description: str,
    after_description: str,
) -> Prompt:
    """Construct a Prompt object from a source snippet."""
    node_name = transform_type.plaintext_name()
    return Prompt(
        f"""### Python {node_name} {before_description}
{before_text}

### The same Python {node_name} {after_description}
{after_text}

### Python {node_name} {before_description}
{snippet}
### End of {node_name}

### Now rewrite the Python {node_name} {after_description}
""",
        max_tokens=len(snippet) // 2,
        stop=f"### End of {node_name}",
    )


def resolve_prompt(prompt: Prompt) -> str:
    """Generate a completion for a prompt."""
    response = api.create_completion(
        prompt=prompt.text,
        max_tokens=prompt.max_tokens,
        stop=prompt.stop,
        temperature=0,
        model="text-davinci-002",
    )
    for choice in response["choices"]:
        return cast(str, choice["text"])
    else:
        raise Exception("Request failed to generate choices.")
