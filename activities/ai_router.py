from .local_llm import generate_local_response



def classify_complexity(prompt: str) -> str:
    """Classify a Knit activity request using simple rules."""
    prompt = prompt.strip().lower()

    complex_indicators = [
        "compare",
        "budget",
        "schedule",
        "accessibility",
        "personalized",
        "personalised",
        "multiple",
        "limited time",
        "explain why",
        "specific preferences",
        "constraints",
    ]

    matches = sum(
        indicator in prompt
        for indicator in complex_indicators
    )

    if len(prompt) > 350 or matches >= 2:
        return "complex"

    if len(prompt) > 150 or matches == 1:
        return "medium"

    return "simple"


def choose_model(
    prompt: str,
    scenario: str = "normal",
    system_load: float = 0.0,
    daily_requests: int = 0,
) -> dict:
    """Choose the best model for a Knit activity request."""

    complexity = classify_complexity(prompt)

    if scenario == "overload" or system_load >= 0.85:
        if complexity == "complex":
            return {
                "model": "hosted",
                "reason": "Hosted model selected for a complex request.",
                "complexity": complexity,
            }

        return {
            "model": "local",
            "reason": "Local model selected during system overload.",
            "complexity": complexity,
        }

    if scenario == "peak" or daily_requests >= 10000:
        if complexity == "complex":
            return {
                "model": "hosted",
                "reason": "Hosted model selected for complex reasoning.",
                "complexity": complexity,
            }

        return {
            "model": "local",
            "reason": "Local model selected to reduce API traffic.",
            "complexity": complexity,
        }

    if scenario == "cost":
        if complexity == "complex":
            return {
                "model": "hosted",
                "reason": "Hosted model retained for complex requests.",
                "complexity": complexity,
            }

        return {
            "model": "local",
            "reason": "Local model selected to reduce API costs.",
            "complexity": complexity,
        }

    if scenario == "complex" or complexity == "complex":
        return {
            "model": "hosted",
            "reason": "Hosted model selected for complex reasoning.",
            "complexity": complexity,
        }

    return {
        "model": "local",
        "reason": "Local model selected for a routine request.",
        "complexity": complexity,
    }


def generate_routed_response(
    prompt: str,
    scenario: str = "normal",
    system_load: float = 0.0,
    daily_requests: int = 0,
) -> dict:
    """Select a model and generate an activity recommendation."""

    cleaned_prompt = prompt.strip()

    if not cleaned_prompt:
        return {
            "status": "error",
            "message": "Please describe the activities you are looking for.",
        }

    if len(cleaned_prompt) > 2000:
        return {
            "status": "error",
            "message": "Your request must be 2000 characters or fewer.",
        }

    routing = choose_model(
        cleaned_prompt,
        scenario=scenario,
        system_load=system_load,
        daily_requests=daily_requests,
    )

    try:
        if routing["model"] == "local":
            response_text = generate_local_response(cleaned_prompt)

        else:
            from .hybrid_pipeline import run_hybrid_pipeline
            hosted_result = run_hybrid_pipeline(cleaned_prompt)

            if hosted_result.get("status") != "success":
                # Use the local model if hosted generation fails.
                response_text = generate_local_response(cleaned_prompt)
                routing["fallback"] = "local"
            else:
                response_text = hosted_result["api_output"]

        return {
            "status": "success",
            "model_used": routing.get("fallback", routing["model"]),
            "complexity": routing["complexity"],
            "reason": routing["reason"],
            "response": response_text,
        }

    except Exception as e:
        return {
            "status": "error",
            "model_selected": routing["model"],
            "message": str(e),
        }
