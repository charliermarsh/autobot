# autobot

[![PyPI version](https://badge.fury.io/py/autobot-ml.svg)](https://badge.fury.io/py/autobot-ml)

An automated code refactoring tool powered by GPT-3. Like GitHub Copilot, for your existing
codebase.

<p align="center">
  <img alt="Sorting class attributes" src="https://user-images.githubusercontent.com/1309177/190036496-28d096f1-fde5-47af-a936-235b3802dc07.gif">
</p>

Autobot takes an example change as input and generates patches for you to review by scanning your
codebase for similar code blocks and "applying" that change to the existing source code.

See more examples on <a href="https://twitter.com/charliermarsh/status/1569329858475425792" target="_blank">
Twitter</a>, or read the <a href="https://notes.crmarsh.com/building-large-language-model-powered-applications" target="_blank">
blog post</a>.

_N.B. Autobot is a prototype and isn't recommended for use of large codebases. See: ["Limitations"](#Limitations)._

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

In the second step (`autobot review`), we review the patches that Autobot generated and, for each
suggested change, either apply it to the codebase or reject the patch entirely.

Autobot ships with several schematics that you can use out-of-the-box:

- `assert_equals`
- `convert_to_dataclass`
- `numpy_builtin_aliases`
- `print_statement`
- `sorted_attributes`
- `standard_library_generics`
- `unnecessary_f_strings`
- `use_generator`
- `useless_object_inheritance`

For example: to remove any usages of NumPy's deprecated `np.int` and associated aliases, we'd first
run `autobot run numpy_builtin_aliases ./path/to/main.py`, followed by `autobot review`.

The `schematic` argument to `autobot run` can either reference a directory within `schematics` (like
`numpy_builtin_aliases`, above) or a path to a user-defined schematic directory on-disk.

### Implementing a novel refactor

Every refactor facilitated by Autobot requires a "schematic". Autobot ships with a few schematics
in the `schematics` directory, but it's intended to be used with user-provided schematics.

A schematic is a directory containing two files:

1. `before.py`: A code snippet demonstrating the "before" state of the refactor.
2. `after.py`: A code snippet demonstrating the "after" state of the refactor.

Each file is expected to consist of a brief top-level docstring describing the "before" and "after"
states, followed by a single function or class.

For example: in Python 3, `class Foo(object)` is equivalent to `class Foo`. To automatically remove
those useless object inheritances from our codebase, we'd create a `useless_object_inheritance`
directory, and add the above files.

```python
# before.py
"""...with object inheritance."""
class Foo(Bar, object):
    def __init__(self, x: int) -> None:
        self.x = x

```

```python
# after.py
"""...without object inheritance."""
class Foo(Bar):
    def __init__(self, x: int) -> None:
        self.x = x

```

We'd then run `autobot run ./useless_object_inheritance /path/to/file/or/directory` to generate
patches, followed by `autobot review` to apply or reject the suggested changes.

## Limitations

1. Running Autobot consumes OpenAI credits and thus could cost you money. Be careful!
2. By default, Autobot uses OpenAI's `text-davinci-002` model, though `autobot run` accepts a
   `--model` parameter, allowing you to select an alternative OpenAI model. Note, though, that
   OpenAI's Codex models are currently in a private beta, so `code-davinci-002` and friends may
   error for you.
4. To speed up execution, Autobot calls out to the OpenAI API in parallel. If you haven't upgraded
   to a paid account, you may hit rate-limit errors. You can pass `--nthreads 1` to `autobot run`
   to disable multi-threading. Running Autobot over large codebases is not recommended (yet).
5. Depending on the transform type, Autobot will attempt to generate a patch for every function or
   every
   class. Any function or class that's "too long" for GPT-3's maximum prompt size will be skipped.
6. Autobot isn't smart enough to handle nested functions (or nested classes), so nested functions
   will likely be processed and appear twice.
7. Autobot only supports Python code for now. (Autobot relies on parsing the AST to extract relevant
   code snippets, so additional languages require extending AST support.)

## Roadmap

1. **Multi-language support.** Autobot only supports Python code for now. Extending to
   multi-language support, at least with the current algorithm, will require supporting additional
   AST parsers. The most likely outcome here will either be to leverage [`tree-sitter`](https://github.com/tree-sitter/tree-sitter).
2. **Supporting large codebases.** What would it take to run Autobot over hundreds of thousands of
   lines of code?

## License

MIT
