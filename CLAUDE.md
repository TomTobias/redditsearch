# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`redditsearch` is a Python 3.14 application for searching Reddit content. This is an early-stage project with minimal infrastructure currently in place.

## Development Commands

### Running the Application
```bash
python main.py
```

### Notes
- No testing framework is currently configured
- No linting or formatting tools are currently configured
- No build step is required for this project

## Project Structure

This is currently a simple single-file application:
- **Entry point:** [main.py](main.py) - Contains the `main()` function
- **Package configuration:** [pyproject.toml](pyproject.toml) - Uses modern Python packaging (PEP 517/518)
- **Python version:** 3.14 (specified in `.python-version`)

## Dependencies

The project currently has no external dependencies (`dependencies = []` in pyproject.toml).
