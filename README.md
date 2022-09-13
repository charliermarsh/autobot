# autobot

An automated code refactoring tool powered by GPT-3. Like GitHub Copilot, for your existing
codebase.

## Getting started

First, add a `.env` file to the root directory, with a structure like this:

```
OPENAI_ORGANIZATION=${YOUR_OPENAI_ORGANIZATION}
OPENAI_API_KEY=${YOUR_OPENAI_API_KEY}
```

Then, run `poetry install`.

## Example usage

### Removing useless object inheritance

```shell
python -m autobot useless_object_inheritance schematics/useless_object_inheritance/
```

### Removing print statements

```shell
python -m autobot print_statement schematics/print_statement/
```

### Rename `self.assertEquals` to `self.assertEqual`

```shell
python -m autobot assert_equals schematics/assert_equals/
```

### Remove unnecessary f-strings

```shell
python -m autobot unnecessary_f_strings schematics/unnecessary_f_strings/
```

### Migrating to standard library generics

```shell
python -m autobot standard_library_generics schematics/standard_library_generics/
```

## License

MIT
