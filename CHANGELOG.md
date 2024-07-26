# Unreleased

- Major refactor. CLI is now based on typer.
- Adds two cli options: `--invert-image` that can be used be invert images with
  dark-background and `--remove-grid` that can be used to remove grids (default
  `False`). 

# [0.3.0] 2024-07-14

It is a maintenance release. The minimum supported python version is 3.9.

- Update to dependencies.

# [0.2.3] 2022-11-06

- Removed loguru. #11
- Drop support of python3.7.
- Fixed #14
- Better Windows support.

# 2021-06-30: v0.2.2

- Fixed regression: axis transformation was broken.

# 2021-06-30: v0.2.1

- Support for grids in the plots.
- Refactor. `poetry` based development and package management.
