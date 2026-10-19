## Part 2: System Description & AI Architecture

### 1. Data Input
* **Capture Mechanism:** User text is captured through a frontend form interface rendered via Django templates (`hybrid_ai.html`).
* **Transmission Protocol:** The data is submitted to the backend route (`/hybrid-ai/`) via an authenticated HTTP `POST` request.
* **Authentication & Integrity:** The endpoint is secured using Django's `@login_required` decorator to restrict access to authenticated sessions, and submissions are protected against Cross-Site Request Forgery via Django’s `{% csrf_token %}` mechanism.

### 2. Preprocessing
Before passing raw user input into our dual-stage model architecture, the server applies strict sanitization:
* **Whitespace Normalization:** The input string is stripped of leading and trailing whitespace to eliminate empty padding and accidental whitespace payloads (`cleaned_text = user_input.strip()`).
* **Input Validation & Bound Checking:** The pipeline checks for non-empty text and enforces a strict ceiling of 2,000 characters to prevent buffer overflow attacks and unnecessary compute overhead.
* **Sequence Truncation:** For local model inference, the text is sliced to the first 512 characters/tokens (`cleaned_text[:512]`) to adhere to the maximum context window of the local transformer architecture without causing positional embedding runtime errors.

### 3. Safety Guardrails & Robustness
Our implementation utilizes a multi-layered defense strategy spanning input screening, compute filtering, and network fault tolerance:

* **Stage 1 (Local Hugging Face Compute Filter):**
  * We deployed a local `distilbert/distilbert-base-uncased-finetuned-sst-2-english` classification pipeline directly on the Django application server.
  * The local model evaluates the emotional valence and potential toxicity of the user input.
  * **Automated Circuit Breaker:** If the local classifier flags the content as `NEGATIVE` with a confidence score exceeding $0.90$, the pipeline halts execution immediately. This acts as a cost-effective firewall, rejecting abusive or toxic inputs locally and preventing unnecessary, billable external API requests.

* **Stage 2 (External API Generation with Sandboxed Exceptions):**
  * Submissions that successfully pass the local guardrail are forwarded to the Groq Cloud Inference API running an open-weight LLM (`qwen/qwen3.8-27b`).
  * **System Instruction Sandboxing:** Strict system instructions enforce role adherence ("You are an intelligent text refinement assistant..."), constraining the model to structured text rewriting and preventing prompt injection drift.
  * **Fault Tolerance & Broken Output Handling:** External API network calls are encapsulated in strict `try/except` blocks. If the external provider experiences network latency, rate limits (HTTP 429), or missing resources (HTTP 404), the exception is caught gracefully. Instead of raising an unhandled HTTP 500 error that crashes the Django server, the view returns a structured `partial_success` status payload containing the local analysis alongside an explicit error description for user visibility.