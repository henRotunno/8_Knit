import os
from functools import lru_cache


@lru_cache(maxsize=1)
def get_classifier():
    from transformers import pipeline

    return pipeline(
        "text-classification",
        model="distilbert/distilbert-base-uncased-finetuned-sst-2-english",
    )


def run_hybrid_pipeline(user_input: str) -> dict:
    cleaned_text = user_input.strip()
    if not cleaned_text:
        return {"status": "error", "message": "Input cannot be empty."}

    if len(cleaned_text) > 2000:
        return {"status": "error", "message": "Input exceeds 2000 character limit."}

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return {"status": "error", "message": "The optional hosted feature requires a Groq API key."}

    # Stage 1: Local Pre-filter Guardrail
    try:
        local_result = get_classifier()(cleaned_text, truncation=True, max_length=512)[0]
        label = local_result.get("label")
        score = local_result.get("score", 0.0)
    except Exception as e:
        return {"status": "error", "message": f"Local model error: {str(e)}"}

    if label == "NEGATIVE" and score > 0.90:
        return {
            "status": "rejected",
            "local_analysis": {"label": label, "confidence": round(score, 3)},
            "api_output": "Processing halted: Input flagged by local filter as strongly negative in sentiment."
        }

    # Stage 2: External Groq Cloud Generation
    try:
        from groq import Groq

        groq_client = Groq(api_key=api_key, timeout=15.0, max_retries=0)
        completion = groq_client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[
                {
                    "role": "system",
                    "content": "You are an intelligent text refinement assistant. Analyze the user's input, enhance its clarity and tone, and provide a concise summary."
                },
                {"role": "user", "content": cleaned_text}
            ],
            temperature=0.7,
            max_tokens=300
        )
        api_text = completion.choices[0].message.content.strip()

        return {
            "status": "success",
            "local_analysis": {"label": label, "confidence": round(score, 3)},
            "api_output": api_text
        }
    except Exception as e:
        return {
            "status": "partial_success",
            "local_analysis": {"label": label, "confidence": round(score, 3)},
            "api_output": f"External API Error: {str(e)}"
        }
