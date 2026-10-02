# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  answer.py                                         :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: hguesne <hguesne@student.42lehavre.fr>    +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/09/28 20:49:57 by hguesne         #+#    #+#               #
#  Updated: 2026/10/02 18:03:29 by hguesne         ###   ########.fr        #
#                                                                           #
# ************************************************************************* #


"""Answer generation on top of retrieved source snippets."""

from __future__ import annotations
from typing import Any, List
from transformers import AutoModelForCausalLM, AutoTokenizer
from src.cli.search import search

import torch
MODEL_NAME = "Qwen/Qwen3-0.6B"


def load_llm() -> tuple[Any, Any]:
    """Load the default Qwen tokenizer and causal language model."""

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    try:
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            dtype=torch.float16,
            device_map="auto",
        )
    except RuntimeError as exc:
        message = str(exc).lower()
        if "out of memory" not in message and "cuda" not in message:
            raise
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            dtype=torch.float32,
            device_map="cpu",
        )
    return tokenizer, model


def generate_answer(question: str, context_snippets: list[str], tokenizer: Any,
                    model: Any) -> str:
    """Generate a grounded answer from retrieved context snippets."""

    context_str = "\n\n---\n\n".join(context_snippets)

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant answering questions about " +
                "a codebase.\n"
                "Use ONLY the following retrieved snippets to answer. "
                "If the answer cannot be found, state that clearly.\n"
                "Answer in as few words as possible"
            ),
        },
        {
            "role": "user",
            "content": f"Context:\n{context_str}\n\nQuestion: {question}",
        },
    ]

    prompt = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )

    inputs = tokenizer(prompt, return_tensors="pt")
    if hasattr(model, "device"):
        inputs = inputs.to(model.device)
    outputs = model.generate(**inputs, max_new_tokens=256, do_sample=False)

    generated_ids = outputs[0][inputs.input_ids.shape[-1]:]
    raw_answer: str = tokenizer.decode(generated_ids,
                                       skip_special_tokens=True).strip()
    if "</think>" in raw_answer:
        answer = raw_answer.split("</think>")[-1].strip()
    else:
        answer = raw_answer
    return answer


def answer(question: str, k: int = 5) -> str:
    """Retrieve context for one question and return the generated answer."""

    k = min(k, 10)
    context_snippets: List[str]
    tokenizer, model = load_llm()
    temp = search(question, k, printable=0)
    context_snippets = [item.text for item in temp]
    return generate_answer(question, context_snippets, tokenizer, model)
