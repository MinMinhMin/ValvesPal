# VALVESPAL

An app that tracks sales across Steam and other stores, while also analyzing data about games such as prices, player counts, and more.

## Getting Started

Follow the steps below to set up the project. You can use **Poetry** to manage dependencies and virtual environments or install the required packages from the `requirements.txt` file directly.

### Prerequisites

- **Python 3.11+**
- **Poetry** (optional, for dependency management and virtual environment setup)
- **Chrome** (Sorry :D)

### Installation

#### Option 1: Using Poetry

1. **Install Poetry**:
   If Poetry is not installed, follow the [Poetry installation guide](https://python-poetry.org/docs/#installation) or just:

   ```batch
   pip install poetry
   ```

2. **Clone the Repository**:

   ```bash
   git clone https://github.com/MinMinhMin/ValvesPal.git
   cd ValvesPal
   ```

3. **Install dependencies**:
   ```batch
   poetry install
   ```

#### Option 2: Using requirements.txt

If you are not using venv or are using a different dependency manager, use this instead.

## P/S:

You must host a local server on port 5500 to visualize charts.

```batch
   python -m http.server 5500
```

or simply download the Live Server extension in Visual Studio Code, then

```batch
   live-server --port=5500
```
