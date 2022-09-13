# autobot

An automated code refactoring tool powered by GPT-3. Like GitHub Copilot, for your existing
codebase.

Autobot takes an example change as input and generates patches for you to review by scanning your
codebase for similar code blocks and "applying" that change to the existing source code.

## Getting started

Autobot is available as [`autobot-ml`](https://pypi.org/project/autobot-ml/) on PyPI:

```shell
pip install autobot-ml
```

Autobot depends on the [OpenAI API](https://openai.com/api/) and, in particular, expects your OpenAI
organization ID and API key to be exposed as the `OPENAI_ORGANIZATION` and `OPENAI_API_KEY`
environment variables, respectively.

Autobot can also read from a `.env` file:

```
OPENAI_ORGANIZATION=${YOUR_OPENAI_ORGANIZATION}
OPENAI_API_KEY=${YOUR_OPENAI_API_KEY}
```

## Example usage

_TL;DR: Autobot is a command-line tool. To generate patches, use `autobot run`; to review the
generated patches, use `autobot review`._

Autobot is designed around a two-step workflow.

In the first step (`autobot run {schematic} {files_to_analyze}`), we point Autobot to (1) the
"schematic" that defines our desired change and (2) the files to which the change should be
applied.

In the second step (`autobot review`), we review the patches that Autobot generated and,
for each suggested change, either apply it to the codebase or reject it.

For example: to remove any usages of NumPy's deprecated `np.int` and associated aliases, we'd first
run `autobot run ./schematics/numpy_builtin_aliases ./path/to/main.py`, followed by
`autobot review`.

### Implementing a novel refactor

Every refactor facilitated by Autobot requires a "schematic". Autobot ships with a few example
schematics in the `schematics` directory, but it's intended to be used with user-provided
schematics.

A schematic is a directory containing three files:

1. `before.py`: A code snippet demonstrating the "before" state of the refactor.
2. `after.py`: A code snippet demonstrating the "after" state of the refactor.
3. `autobot.json`: A JSON object containing a plaintext description of the
   before (`before_description`) and after (`after_description`) states, along with
   the `transform_type` ("Function" or "Class").

For example: in Python 3, `class Foo(object)` is equivalent to `class Foo`. To automatically remove
those useless object inheritances from our codebase, we'd create a `useless_object_inheritance`
directory, and add the above files.

```python
# before.py
class Foo(Bar, object):
    def __init__(self, x: int) -> None:
        self.x = x
```

```python
# after.py
class Foo(Bar):
    def __init__(self, x: int) -> None:
        self.x = x
```

```json
// autobot.json
{
    "before_description": "with object inheritance",
    "after_description": "without object inheritance",
    "transform_type": "Class"
}
```

We'd then run `autobot run useless_object_inheritance /path/to/file/or/directory` to generate
patches, followed by `autobot review` to apply or reject the suggested changes.

## Limitations

1. To speed up execution, Autobot calls out to the OpenAI API in parallel. If you haven't upgraded
   to a paid account, you may hit rate-limit errors. You can pass `--nthreads 1` to `autobot run`
   to disable multi-threading.
2. Depending on the transform type, Autobot will either generate a patch for every function or every
   class. Any function or class that's "too long" will be GPT-3's maximum prompt size,

## License

MIT
