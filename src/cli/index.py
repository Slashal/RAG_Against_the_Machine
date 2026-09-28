# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  index.py                                          :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: hguesne <hguesne@student.42lehavre.fr>    +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/09/28 17:56:19 by hguesne         #+#    #+#               #
#  Updated: 2026/09/28 18:34:25 by hguesne         ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

from pathlib import Path
from typing import List, Tuple, Dict
from tqdm import tqdm
from src.cli.class_sub import MinimalSource
from rank_bm25 import BM25Okapi
import pickle
import ast
import re


def tokenize(text: str) -> List[str]:
    """Tokenise le texte pour le modèle BM25."""
    return re.findall(r"\w+", text.lower())


def chunk_python(content: str, max_chunk_size:
                 int = 2000) -> List[Tuple[int, int, str]]:
    """Découpe un fichier Python en extraisant les fonctions
    et classes via AST."""
    chunks = []
    lines = content.splitlines(keepends=True)

    try:
        tree = ast.parse(content)
        # Extraire les fonctions, méthodes et classes top-level
        nodes = [node for node in tree.body if
                 isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                                   ast.ClassDef))]

        if not nodes:
            return chunk_markdown(content, max_chunk_size)

        for node in nodes:
            start_line = node.lineno - 1
            end_line = getattr(node, "end_lineno", len(lines))

            # Calcul des positions exactes en caractères
            start_char = sum(len(lines[i]) for i in range(start_line))
            end_char = sum(len(lines[i]) for i in range(end_line))
            chunk_text = content[start_char:end_char]

            # Vérification de la limite de taille
            if len(chunk_text) <= max_chunk_size:
                chunks.append((start_char, end_char, chunk_text))
            else:
                # Si la fonction/classe est trop longue, sous-découpage
                sub_chunks = chunk_markdown(chunk_text, max_chunk_size)
                for s_start, s_end, s_text in sub_chunks:
                    chunks.append((start_char + s_start,
                                   start_char + s_end, s_text))

    except SyntaxError:
        # Fallback si le fichier Python contient une erreur de syntaxe
        return chunk_markdown(content, max_chunk_size)

    return chunks


def chunk_markdown(content: str, max_chunk_size:
                   int = 2000) -> List[Tuple[int, int, str]]:
    """Découpe un fichier Markdown/Texte en respectant la limite de caractères.

    Retourne une liste de tuples: (first_character_index,
    last_character_index, text)
    """
    chunks = []
    start = 0
    length = len(content)

    while start < length:
        end = min(start + max_chunk_size, length)

        # Si on n'est pas à la fin, on cherche le dernier saut de ligne pour
        # ne pas couper une phrase
        if end < length:
            last_newline = content.rfind("\n", start, end)
            if last_newline > start:
                end = last_newline + 1

        chunk_text = content[start:end]
        chunks.append((start, end, chunk_text))
        start = end

    return chunks


def indexer(max_chunk_size: int = 2000, raw_path: str = "data/raw",
            processed_path: str = "data/processed") -> None:
    raw_chunks = []
    all_chunks: List[Dict[str, object]] = []
    corpus_tokens: List[List[str]] = []
    chunk_data = MinimalSource()
    try:
        file = [f for f in Path(raw_path).rglob("*") if f.is_file()]
        Path(processed_path).mkdir(parents=True, exist_ok=True)
        for fi in tqdm(file, bar_format='[{elapsed}<{remaining}] ' +
                                        '{n_fmt}/{total_fmt} | {l_bar}{bar} ' +
                                        '{rate_fmt}{postfix}', colour='yellow',
                                        desc="Chunking files"):
            if not fi.is_file():
                continue

            if fi.suffix in [".txt", ".md"]:
                with open(fi, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
                    raw_chunks = chunk_markdown(text, max_chunk_size)

            elif fi.suffix == ".py":
                with open(fi, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
                    raw_chunks = chunk_python(text, max_chunk_size)
            else:
                continue
            for start, end, text in raw_chunks:
                chunk_data = {
                    "file_path": str(fi),
                    "first_character_index": start,
                    "last_character_index": end,
                    "text": text
                }
                all_chunks.append(chunk_data)
                corpus_tokens.append(tokenize(text))

        if not corpus_tokens:
            raise ValueError("⚠️ Aucun fichier valide trouvé à indexer.")
        bm25_model = BM25Okapi(corpus_tokens)

        output_file = processed_path + "/" + "bm25_index.pkl"
        with open(output_file, "wb") as f:
            pickle.dump({"bm25": bm25_model, "chunks": all_chunks}, f)

        print(f"✅ Indexation terminée ! {len(all_chunks)} " +
              f"chunks sauvegardés sous {output_file}")
    except Exception as e:
        print(f"❌ Une erreur est survenue lors de l'indexation : {e}")
        raise
