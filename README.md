*This project has been created as part of the 42 curriculum by hguesne.*

# RAG Against the Machine

## Description

This project implements a retrieval-augmented generation pipeline over the provided vLLM repository.
It indexes the corpus, retrieves the most relevant source snippets for a question, and uses Qwen/Qwen3-0.6B to generate grounded answers.

## Instructions

Requirements:

- Python 3.10+
- `uv`

Install dependencies:

```bash
uv sync
```

Run the project:

```bash
uv run python -m src index --max_chunk_size 2000
uv run python -m src search "your question" --k 5
uv run python -m src search_dataset --dataset_path data/datasets/UnansweredQuestions/dataset_code_public.json --k 5 --save_directory data/output/search_results/UnansweredQuestions
uv run python -m src answer "your question" --k 5
uv run python -m src answer_dataset --student_search_results_path data/output/search_results/AnsweredQuestions/answer_dataset.json --save_directory data/output/search_results_and_answer/AnsweredQuestions
uv run python -m src evaluate --student_search_results_path path/to/search_results.json --dataset_path path/to/dataset.json
uv run python -m src serve --host 127.0.0.1 --port 8080
```

Run the checks:

```bash
make lint
```

## System Architecture

The pipeline has four stages:

1. Indexing: walk `data/raw`, chunk Markdown and Python files differently, and build a BM25 index.
2. Retrieval: score the index against a query and return the top-k source spans.
3. Answer generation: feed the retrieved snippets to Qwen/Qwen3-0.6B and generate a grounded answer.
4. Evaluation: compare retrieved spans against reference answers with a recall@k-style check.

## Chunking Strategy

Markdown and text files are chunked by paragraph and line boundaries, while Python files are chunked from AST-level blocks such as functions and classes.
If a chunk is larger than the configured maximum size, it is split further so no retrieved span exceeds the limit.

## Retrieval Method

The project uses BM25 for lexical retrieval.
Each chunk is tokenized into a normalized bag of words, and the top-k documents are ranked by BM25 score.

## Performance Analysis

The target constraints from the subject are:

- indexing in at most 5 minutes
- retrieval over 200 questions in at most 90 seconds
- recall@5 of at least 80% on docs questions and 50% on code questions

The current implementation is designed to stay within the allowed chunk size and to keep retrieval simple and fast.

## Design Decisions

- Pydantic is used for the data models exchanged between stages.
- Python Fire exposes the command-line interface.
- tqdm provides progress bars for long-running operations.
- The default answer generation model is Qwen/Qwen3-0.6B, as required.

## Challenges Faced

- Keeping chunk boundaries aligned with source locations while avoiding oversize spans.
- Preserving exact `file_path` values so graded retrieval matches the corpus verbatim.
- Handling malformed datasets and empty queries without crashing.

## Example Usage

```bash
uv run python -m src index --max_chunk_size 2000
uv run python -m src search "How is the OpenAI server configured?" --k 5
uv run python -m src search_dataset --dataset_path data/datasets/UnansweredQuestions/dataset_code_public.json --k 5 --save_directory data/output/search_results/UnansweredQuestions
uv run python -m src answer_dataset --student_search_results_path data/output/search_results/AnsweredQuestions/answer_dataset.json --save_directory data/output/search_results_and_answer/AnsweredQuestions
```

## Local HTTP API

The project also exposes a small HTTP API for driving search and answer requests without the CLI.

Start it with:

```bash
uv run python -m src serve --host 127.0.0.1 --port 8080
```

Available endpoints:

- `GET /health`
- `POST /search` with JSON body `{"query": "...", "k": 5}`
- `POST /answer` with JSON body `{"query": "...", "k": 5}`

Example request:

```bash
curl -s http://127.0.0.1:8080/search \
	-H 'Content-Type: application/json' \
	-d '{"query":"How is the OpenAI server configured?","k":5}'
```

## Resources

- BM25 literature and reference implementations
- Python Fire documentation
- tqdm documentation
- Pydantic documentation
- Qwen/Qwen3-0.6B model documentation

AI was used to:
- Draft the README documentation text
- Test edge cases in the retrieval pipeline (empty queries, malformed inputs)
- Generate example usage commands
