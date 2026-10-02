# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  index.py                                          :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: hguesne <hguesne@student.42lehavre.fr>    +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/09/28 17:56:19 by hguesne         #+#    #+#               #
#  Updated: 2026/10/02 16:31:46 by hguesne         ###   ########.fr        #
#                                                                           #
# ************************************************************************* #
from pathlib import Path
from typing import List, Tuple

import ast
import pickle
import re

from rank_bm25 import BM25Plus
from tqdm import tqdm

from src.cli.class_sub import MinimalSource


def tokenize(text: str) -> List[str]:
    text = re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', text)
    words = re.findall(r"\w+", text.lower())
    tokens = []
    for w in words:
        tokens.append(w)
        if '_' in w:
            tokens.extend([sub for sub in w.split('_') if len(sub) > 1])
    return tokens


def chunk_markdown(content: str, max_chunk_size: int = 2000,
                   overlap_ratio: float = 0.10) -> List[Tuple[int, int, str]]:
    """Découpe intelligente du texte/markdown en respectant la structure."""
    chunks = []
    start = 0
    length = len(content)
    overlap = int(max_chunk_size * overlap_ratio)

    while start < length:
        end = min(start + max_chunk_size, length)

        if end < length:
            # 1. On cherche d'abord un titre Markdown
            title_match = re.search(r'\n(?=#{1,6}\s)', content[start:end])
            if title_match and title_match.start() > start + 200:
                end = title_match.start() + 1
            else:
                # 2. Sinon, on cherche une fin de paragraphe (double saut de ligne)
                last_double_newline = content.rfind("\n\n", start, end)
                if last_double_newline > start + 200:
                    end = last_double_newline + 2
                else:
                    # 3. Sinon, un saut de ligne simple
                    last_newline = content.rfind("\n", start, end)
                    if last_newline > start:
                        end = last_newline + 1

        chunk_text = content[start:end]
        if chunk_text.strip():
            chunks.append((start, end, chunk_text))

        if end >= length:
            break

        start = max(start + 1, end - overlap)

    return chunks


def chunk_python(content: str, max_chunk_size: int = 2000,
                 overlap_ratio: float = 0.10) -> List[Tuple[int, int, str]]:
    """Découpe du code Python par AST ou par fenêtre glissante avec chevauchement à 10%."""
    chunks = []
    lines = content.splitlines(keepends=True)

    try:
        tree = ast.parse(content)
        nodes = [node for node in tree.body if
                 isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]

        if not nodes:
            return chunk_markdown(content, max_chunk_size, overlap_ratio)

        for node in nodes:
            start_line = node.lineno - 1
            end_line = getattr(node, "end_lineno", len(lines))

            # Calcul des positions exactes en caractères
            start_char = sum(len(lines[i]) for i in range(start_line))
            end_char = sum(len(lines[i]) for i in range(end_line))
            chunk_text = content[start_char:end_char]

            # Si la taille du nœud respecte la limite
            if len(chunk_text) <= max_chunk_size:
                chunks.append((start_char, end_char, chunk_text))
            else:
                # Sous-découpage avec chevauchement dynamique si la fonction/classe est trop grande
                sub_chunks = chunk_markdown(chunk_text, max_chunk_size, overlap_ratio)
                for s_start, s_end, s_text in sub_chunks:
                    chunks.append((start_char + s_start,
                                   start_char + s_end, s_text))

    except SyntaxError:
        # Fallback si erreur de syntaxe dans le fichier Python
        return chunk_markdown(content, max_chunk_size, overlap_ratio)

    return chunks


def indexer(max_chunk_size: int = 2000, raw_path: str = "data/raw",
            processed_path: str = "data/processed") -> None:
    raw_chunks: List[Tuple[int, int, str]] = []
    all_chunks: List[MinimalSource] = []
    corpus_tokens: List[List[str]] = []
    try:
        file_paths = [f for f in Path(raw_path).rglob("*") if f.is_file()]
        Path(processed_path).mkdir(parents=True, exist_ok=True)
        for fi in tqdm(file_paths, bar_format='[{elapsed}<{remaining}] ' +
                                        '{n_fmt}/{total_fmt} | {l_bar}{bar} ' +
                                        '{rate_fmt}{postfix}', colour='yellow',
                                        desc="Chunking files"):
            if not fi.is_file():
                continue

            if fi.suffix in [".txt", ".md"]:
                with open(fi, "r", encoding="utf-8", errors="ignore") as input_file:
                    text = input_file.read()
                    raw_chunks = chunk_markdown(text, max_chunk_size)

            elif fi.suffix == ".py":
                with open(fi, "r", encoding="utf-8", errors="ignore") as input_file:
                    text = input_file.read()
                    raw_chunks = chunk_python(text, max_chunk_size)
            else:
                continue
            for start, end, text in raw_chunks:
                chunk_data = MinimalSource(
                    file_path=str(fi),
                    first_character_index=start,
                    last_character_index=end,
                    text=text,
                )
                all_chunks.append(chunk_data)
                corpus_tokens.append(tokenize(text))

        if not corpus_tokens:
            raise ValueError("⚠️ Aucun fichier valide trouvé à indexer.")
        bm25_model = BM25Plus(corpus_tokens)

        output_file = str(Path(processed_path) / "bm25_index.pkl")
        with open(output_file, "wb") as output_handle:
            pickle.dump({"bm25": bm25_model, "chunks": all_chunks}, output_handle)

        print(f"✅ Indexation terminée ! {len(all_chunks)} " +
              f"chunks sauvegardés sous {output_file}")
    except Exception as e:
        print(f"❌ Une erreur est survenue lors de l'indexation : {e}")
        raise
