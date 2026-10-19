import torch
from functools import lru_cache
from transformers import pipeline


MODEL_NAME = "Qwen/Qwen2.5-1.5B-Instruct"


@lru_cache(maxsize=1)
def get_generator():
    """
    Load the local Hugging Face model once and reuse it
    for later requests.
    """
    return pipeline(
        "text-generation",
        model=MODEL_NAME,
        tokenizer=MODEL_NAME,
        device=-1,  # Run locally on CPU
        model_kwargs={
            "torch_dtype": torch.float32,
        },
    )


def generate_local_response(user_input: str) -> str:
    cleaned_input = user_input.strip()

    if not cleaned_input:
        return "Please enter a description of what you would like to do."

    messages = [
        {
            "role": "system",
            "content": (
                "You are a friendly activity recommendation assistant for Knit, "
                "a weekend activity planning website. "
                "Read the user's request carefully and follow all stated preferences "
                "and constraints. Recommend exactly 3 distinct activities. "
                "Write in a natural, conversational tone, as if you were giving "
                "suggestions to a friend. Connect the ideas smoothly instead of "
                "listing them mechanically. Briefly explain why each activity fits "
                "the user's request. Keep the whole response under 90 words. "
                "Do not use markdown, bullet points, or numbered lists."
            ),
        },
        {
            "role": "user",
            "content": cleaned_input,
        },
    ]
    generator = get_generator()

    result = generator(
        messages,
        max_new_tokens=120,
        do_sample=False,
    )

    generated = result[0]["generated_text"]

    if isinstance(generated, list):
        return generated[-1]["content"].strip()

    return str(generated).strip()