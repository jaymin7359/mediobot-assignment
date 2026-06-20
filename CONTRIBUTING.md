# Contributing to the Project

Thank you for considering contributing to this repository! We welcome contributions from the community and aim to make the process as smooth as possible. Please read the following guidelines before getting started.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Submitting Pull Requests](#submitting-pull-requests)
- [Development Setup](#development-setup)
- [Commit Message Style](#commit-message-style)
- [Testing](#testing)
- [Documentation](#documentation)
- [License](#license)

## Code of Conduct

Please note that this project adheres to the [Code of Conduct](data/general/code_of_conduct.pdf). By participating, you are expected to uphold this code.

## How to Contribute

### Reporting Bugs

1. Search the existing issues to see if the bug has already been reported.
2. If not, open a new issue with:
   - A clear title.
   - Steps to reproduce the bug.
   - Expected vs. actual behavior.
   - Any relevant logs or screenshots.

### Suggesting Enhancements

1. Search the existing issues to avoid duplicates.
2. Open a new issue describing the proposed change, its motivation, and any relevant design considerations.

### Submitting Pull Requests

1. **Fork** the repository.
2. **Clone** your fork locally.
3. Create a new branch for your work:
   ```bash
   git checkout -b my-feature-branch
   ```
4. Make your changes, ensuring the code follows the existing style and passes all tests.
5. Commit your changes following the [Commit Message Style](#commit-message-style).
6. Push the branch to your fork:
   ```bash
   git push origin my-feature-branch
   ```
7. Open a Pull Request (PR) against the `main` branch of the upstream repository.
   - Include a clear description of what the PR does.
   - Reference any related issues (e.g., `Closes #42`).
   - Ensure the PR passes all CI checks.

## Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/your-repo.git
   cd your-repo
   ```
2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows use `venv\Scripts\activate`
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the application** (backend example):
   ```bash
   uvicorn backend.main:app --reload
   ```
5. **Run the frontend** (if applicable):
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Commit Message Style

We follow the Conventional Commits specification. A typical commit message looks like:

```
<type>(<scope>): <subject>

<body>

<footer>
```

- **type**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, etc.
- **scope** (optional): the area of the codebase, e.g., `backend`, `frontend`.
- **subject**: a short description (max 72 characters).
- **body** (optional): more detailed explanation.
- **footer** (optional): references to issues (`Closes #123`).

## Testing

- Backend tests (if any) can be run with:
  ```bash
  pytest
  ```
- Ensure all new code is covered by tests where appropriate.

## Documentation

- Update the `README.md` or any relevant docs when adding new features.
- Keep documentation clear, concise, and up‑to‑date.

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for your contributions!
