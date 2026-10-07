# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  answer_dataset.py                                 :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: hguesne <hguesne@student.42lehavre.fr>    +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/09/28 20:48:15 by hguesne         #+#    #+#               #
#  Updated: 2026/10/07 16:17:58 by hguesne         ###   ########.fr        #
#                                                                           #
# ************************************************************************* #
"""Batch answer generation for previously retrieved search results."""

from pathlib import Path
from typing import List
from tqdm import tqdm
from src.cli.answer import generate_answer, load_llm
from src.cli.class_sub import StudentSearchResultsAndAnswer
from src.cli.class_sub import MinimalAnswer

import json


def answer_dataset(student_search_results_path: str,
                   save_directory: str) -> None:
    """Generate answers for a search-results dataset
    and persist JSON output."""

    try:
        search_result: List[MinimalAnswer] = []

        # Chargement du dataset
        with open(student_search_results_path, 'r') as f:
            dataset = json.load(f)

        # Chargement du LLM
        tokenizer, model = load_llm()

        # Définition de k
        k = min(int(dataset['k']), 10)

        # Génération des réponses
        for data in tqdm(dataset['search_results'], desc="Generating answers"):
            question = data['question']
            context_source = []

            # Construction du contexte
            for source in data['retrieved_sources']:
                context_source.append(source['text'])

            # Génération d'une réponse
            answer = MinimalAnswer(answer=generate_answer(question,
                                                          context_source,
                                                          tokenizer,
                                                          model),
                                   **data)
            # Ajout de la réponse au résultat
            search_result.append(answer)

        # Formalisation du résultat à la classe StudentSearchResultsAndAnswer
        result = StudentSearchResultsAndAnswer(search_results=search_result,
                                               k=k)
        # Vérification de l'existance du chemin de sauvegarde,
        # et le créer dans le cas contraire
        output_directory = Path(save_directory)
        output_directory.mkdir(parents=True, exist_ok=True)

        # Sauvegarde du résultat
        output_file = Path(student_search_results_path).name
        with open(output_directory / output_file, 'w') as f:
            json.dump(result.model_dump(), f, indent=2)

    except Exception as e:
        raise Exception(f"Error occurred while processing the dataset: {e}")
