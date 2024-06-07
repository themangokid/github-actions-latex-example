# GitHub Actions LaTeX Example

[![Build](https://github.com/maxkratz/github-actions-latex-example/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/maxkratz/github-actions-latex-example/actions/workflows/ci.yml)

This repository is a minimal example on how to build a LaTeX document using GitHub Actions and Docker.

To minimize LaTeX compile times when running the CI, this repository uses a full [TeX Live](https://tug.org/texlive/) installation based on a [pre-built TeX Live Docker image](https://github.com/maxkratz/docker_texlive), which is available on [Docker Hub](https://hub.docker.com/r/maxkratz/texlive).


## License

This project is licensed unter the [LaTeX Project Public License](./LICENSE).
