# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  index.py                                          :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: hguesne <hguesne@student.42lehavre.fr>    +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/09/28 17:56:19 by hguesne         #+#    #+#               #
#  Updated: 2026/10/07 16:21:19 by hguesne         ###   ########.fr        #
#                                                                           #
# ************************************************************************* #
"""Corpus indexing and chunking utilities for the RAG pipeline."""

from pathlib import Path
from typing import List, Tuple
from rank_bm25 import BM25Plus
from tqdm import tqdm
from src.cli.class_sub import MinimalSource

import ast
import pickle
import re


def tokenize(text: str) -> List[str]:
    """Normalize text into a token list for BM25 indexing."""

    # Séparation des mots en camelCase
    text = re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', text)
    words = re.findall(r"\w+", text.lower())
    tokens = []

    # Séparation des mots par underscore
    for w in words:
        tokens.append(w)
        if '_' in w:
            tokens.extend([sub for sub in w.split('_') if len(sub) > 1])
    return tokens


def chunk_markdown(content: str, max_chunk_size: int = 2000,
                   overlap_ratio: float = 0.10) -> List[Tuple[int, int, str]]:
    """Chunk Markdown or text content while preferring natural boundaries."""
    chunks = []
    start = 0
    length = len(content)

    # Initialisation de la longueur du chevauchement
    overlap = int(max_chunk_size * overlap_ratio)

    while start < length:
        # Définition de la fin du chunk
        end = min(start + max_chunk_size, length)

        if end < length:
            # Recherche d'un \n suivi d'un titre markdown
            title_match = re.search(r'\n(?=#{1,6}\s)', content[start:end])
            # Si le titre est trouvé et qu'il est à plus de 200 caractères
            # du début du chunk, resize le chunk pour s'arreter après \n
            if title_match and title_match.start() > start + 200:
                end = title_match.start() + 1
            else:
                # Cherche un double saut de ligne pour arreter le chunk
                last_double_newline = content.rfind("\n\n", start, end)
                if last_double_newline > start + 200:
                    end = last_double_newline + 2
                else:
                    # Cherche un simple saut de ligne pour arreter le chunk
                    last_newline = content.rfind("\n", start, end)
                    if last_newline > start:
                        end = last_newline + 1

        # Création du chunk et l'ajoute à la liste des chunks
        chunk_text = content[start:end]
        if chunk_text.strip():
            chunks.append((start, end, chunk_text))

        if end >= length:
            break
        # Mise à jour de la position de départ en prenant en compte le
        # chevauchement
        start = max(start + 1, end - overlap)

    return chunks


def chunk_python(content: str, max_chunk_size: int = 2000,
                 overlap_ratio: float = 0.10) -> List[Tuple[int, int, str]]:
    """Chunk Python source using AST blocks, with text fallback when needed."""

    chunks = []

    # Divise le contenu en lignes
    lines = content.splitlines(keepends=True)

    try:
        # Analyse le code Python pour extraire les blocs AST
        # Abstract Syntax Tree découpe le code représente la structure du code
        # sous forme d'arbre
        tree = ast.parse(content)
        # Parcourt les nœuds de l'arbre pour trouver les définitions
        # de fonctions et de classes
        nodes = [node for node in tree.body if
                 isinstance(node, (ast.FunctionDef,
                                   ast.AsyncFunctionDef, ast.ClassDef))]
        if not nodes:
            return chunk_markdown(content, max_chunk_size, overlap_ratio)

        for node in nodes:
            # Récupère les lignes de début et de fin du nœud
            start_line = node.lineno - 1
            end_line = getattr(node, "end_lineno", len(lines))

            # Défini les caractères de début et de fin de chunks
            start_char = sum(len(lines[i]) for i in range(start_line))
            end_char = sum(len(lines[i]) for i in range(end_line))
            chunk_text = content[start_char:end_char]

            # Ajoute le chunk à la liste des chunks
            if len(chunk_text) <= max_chunk_size:
                chunks.append((start_char, end_char, chunk_text))
            else:
                # Si le chunk est trop grand, on le divise en sous-chunks
                sub_chunks = chunk_markdown(chunk_text,
                                            max_chunk_size, overlap_ratio)
                for s_start, s_end, s_text in sub_chunks:
                    chunks.append((start_char + s_start,
                                   start_char + s_end, s_text))

    except SyntaxError:
        return chunk_markdown(content, max_chunk_size, overlap_ratio)

    return chunks


def indexer(max_chunk_size: int = 2000, raw_path: str = "data/raw",
            processed_path: str = "data/processed") -> None:
    """Build and persist the BM25 index for the raw corpus."""

    max_chunk_size = min(max_chunk_size, 2000)
    raw_chunks: List[Tuple[int, int, str]] = []
    all_chunks: List[MinimalSource] = []
    corpus_tokens: List[List[str]] = []

    try:
        # Parcourt les fichiers du répertoire raw
        file_paths = [f for f in Path(raw_path).rglob("*") if f.is_file()]

        # Crée le répertoire processed si nécessaire
        Path(processed_path).mkdir(parents=True, exist_ok=True)

        for fi in tqdm(file_paths,
                       bar_format='[{elapsed}<{remaining}] ' +
                                  '{n_fmt}/{total_fmt} | {l_bar}{bar} ' +
                                  '{rate_fmt}{postfix}', colour='yellow',
                                  desc="Chunking files"):
            if not fi.is_file():
                continue

            # Traitement de fichier texte .txt .md
            if fi.suffix in [".txt", ".md"]:
                with open(fi, "r", encoding="utf-8",
                          errors="ignore") as input_file:
                    text = input_file.read()
                    raw_chunks = chunk_markdown(text, max_chunk_size)

            # Traitement de code python .py
            elif fi.suffix == ".py":
                with open(fi, "r", encoding="utf-8",
                          errors="ignore") as input_file:
                    text = input_file.read()
                    raw_chunks = chunk_python(text, max_chunk_size)

            # Si le fichier n'est pas un .py, .md ou .txt
            # il ne nous intéresse pas
            else:
                continue

            # Ajout des chunks à la liste des chunks
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
            raise ValueError("⚠️ No valid files found to index.")

        # Construction du modèle BM25
        bm25_model = BM25Plus(corpus_tokens)

        # Sauvegarde du modèle dans le format pickle (binaire)
        output_file = str(Path(processed_path) / "bm25_index.pkl")
        with open(output_file, "wb") as output_handle:
            pickle.dump({"bm25": bm25_model,
                         "chunks": all_chunks}, output_handle)

        print(f"✅ Indexing complete! {len(all_chunks)} " +
              f"chunks save as {output_file}")

    except Exception as e:
        print(f"Error occurred during indexing: {e}")
        raise
