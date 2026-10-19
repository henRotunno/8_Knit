import os
from transformers import pipeline
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Initialize External API client
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Initialize Local Hugging Face Model (guardrail / filter)
local_classifier = pipeline(
    "text-classification",
    model="distilbert/distilbert-base-uncased-finetuned-sst-2-english"
)


def run_hybrid_pipeline(user_input: str) -> dict:
    cleaned_text = user_input.strip()
    if not cleaned_text:
        return {"status": "error", "message": "Input cannot be empty."}

    if len(cleaned_text) > 2000:
        return {"status": "error", "message": "Input exceeds 2000 character limit."}

    # Stage 1: Local Pre-filter Guardrail
    try:
        local_result = local_classifier(cleaned_text[:512])[0]
        label = local_result.get("label")
        score = local_result.get("score", 0.0)
    except Exception as e:
        return {"status": "error", "message": f"Local model error: {str(e)}"}

    if label == "NEGATIVE" and score > 0.90:
        return {
            "status": "rejected",
            "local_analysis": {"label": label, "confidence": round(score, 3)},
            "api_output": "Processing halted: Input flagged by local filter as toxic or excessively negative."
        }

    # Stage 2: External Groq Cloud Generation
    try:
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