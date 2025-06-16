# LLM Code Smell Detection Analysis

A tool for analyzing and comparing different LLM-based strategies for detecting code smells in software projects.

## Overview

This project evaluates the effectiveness of different prompting strategies when using Large Language Models (LLMs) to detect code smells. It analyzes code samples for common code smells such as:

- Blob (God Class)
- Data Class
- Long Method
- Feature Envy

The tool uses OpenAI's API to analyze code samples and provides metrics to evaluate the performance of different prompting strategies.

## Features

- Multiple prompting strategies:
    - Zero-shot
    - Few-shot
    - Chain-of-thought
    - Role prompting
- Comprehensive evaluation metrics:
    - Binary classification metrics (Precision, Recall, Specificity, F1 Score)
    - Ordinal evaluation with Weighted Kappa
    - Visual heatmaps for result analysis
- Support for analyzing individual code samples or batch processing
- Caching mechanism to avoid redundant API calls
- SQLite database for storing code samples and analysis results

## Installation

### Prerequisites

- Python 3.12 or higher
- OpenAI API key
- GitHub token (for fetching code samples)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/llm-code-smell-detection-analysis.git
   cd llm-code-smell-detection-analysis
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root with the following variables:
   ```
   OPENAI_API_KEY=your_openai_api_key
   OPENAI_ORGANIZATION=your_openai_organization_id
   OPENAI_PROJECT=your_openai_project_id
   GITHUB_TOKEN=your_github_token
   ```

## Project Structure

- `config/`: Configuration files
- `data/`: Data models and dataset files
    - `MLCQCodeSmellSamples.csv`: Dataset of code smell samples
    - `code_smell.py`: Code smell data model
    - `code_sample.py`: Code sample data model
- `repository/`: GitHub repository interaction
- `services/`: Core analysis services
    - `single_strategy_analyzer.py`: Analyzer for a single prompting strategy
    - `multi_strategy_analyzer.py`: Analyzer for comparing multiple strategies
    - `openai_client.py`: Client for interacting with OpenAI API
- `main.py`: Main entry point for running analyses
- `initialize_db.py`: Script for initializing the database with code samples

## Usage

### Initialize the Database

Before running analyses, you need to initialize the database with code samples:

```bash
python initialize_db.py
```

### Run Analysis

To run a single strategy analysis:

```python
# In main.py
if __name__ == '__main__':
    conn = sqlite3.connect(Config.DB_PATH)
    iterative_strategy_improvement('zero-shot')
    conn.close()
```

To run a multi-strategy analysis:

```python
# In main.py
if __name__ == '__main__':
    conn = sqlite3.connect(Config.DB_PATH)
    analysis()
    conn.close()
```

To run a large-scale analysis:

```python
# In main.py
if __name__ == '__main__':
    conn = sqlite3.connect(Config.DB_PATH)
    big_analysis()
    conn.close()
```

## Configuration

The project configuration is stored in `config/config.py`. Key configuration options include:

- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_ORGANIZATION`: Your OpenAI organization ID
- `OPENAI_PROJECT`: Your OpenAI project ID
- `GITHUB_TOKEN`: Your GitHub token
- `ASSISTANT_ID`: The ID of the OpenAI Assistant to use
- `DB_PATH`: Path to the SQLite database
- `DATASET_PATH`: Path to the dataset CSV file
- `PROMPT_STRATEGIES`: Dictionary mapping strategy names to assistant IDs

## Evaluation Metrics

### Binary Classification

- **Precision**: Ratio of correctly identified code smells to all identified code smells
- **Recall**: Ratio of correctly identified code smells to all actual code smells
- **Specificity**: Ratio of correctly identified non-smells to all actual non-smells
- **F1 Score**: Harmonic mean of precision and recall

### Ordinal Evaluation

- **Weighted Kappa**: Measure of agreement between actual and predicted severity levels
    - Linear Weighted Kappa: Linear weighting of disagreements
    - Quadratic Weighted Kappa: Quadratic weighting of disagreements

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
