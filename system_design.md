# Multi-Model Routing System Design

## 1. Overview

This project implements a multi-model routing strategy for generating activity suggestions. The router evaluates the complexity of a user's prompt and chooses between a local language model and a hosted model. The goal is to balance response quality, latency, and API cost.

## 2. Five System Scenarios

### Scenario 1: Normal Usage

Users submit everyday requests, such as asking for indoor hobbies or activities to do with friends.

- **Routing strategy:** Use the local Qwen2.5-1.5B-Instruct model for simple requests.
- **Expected benefit:** Reduces reliance on hosted API calls and potential API costs.
- **Trade-off:** Local inference may be slow on a CPU.

### Scenario 2: Complex Requests

Users provide multiple preferences or constraints, such as budget, schedule, accessibility, or personalized recommendations.

- **Routing strategy:** Send complex requests to the hosted model.
- **Expected benefit:** Hosted inference may provide more responsive and capable handling of complex requests.
- **Trade-off:** Hosted requests depend on API availability and may incur usage costs.

### Scenario 3: Peak Traffic

Many users submit requests at the same time, increasing demand on the system.

- **Routing strategy:** Prefer local inference for simple and medium requests, and use hosted inference for complex requests.
- **Expected benefit:** Reduces the number of requests sent to the hosted API.
- **Trade-off:** Local inference can become a bottleneck when many requests compete for CPU resources.

### Scenario 4: Cost-Constrained Operation

The system needs to limit hosted API usage.

- **Routing strategy:** Use the local model for simple and medium requests, reserving the hosted model for complex requests.
- **Expected benefit:** Helps control API usage while retaining hosted inference for requests that may need it.
- **Trade-off:** Local inference may take longer and may produce less useful responses for some prompts.

### Scenario 5: System Overload

The system is experiencing high load, represented by a load value of 0.85 or higher.

- **Routing strategy:** Use the local model for simple and medium requests, while retaining hosted inference for complex requests.
- **Expected benefit:** Avoids sending every request to the hosted API.
- **Trade-off:** Local processing can also slow down under heavy CPU load.

## 3. Routing Strategy

The router classifies prompts as simple, medium, or complex using prompt length and complexity-related keywords. It then considers the operating scenario, system load, and daily request count to select a model.

| Scenario | Simple/Medium Requests | Complex Requests |
|---|---|---|
| Normal | Local model | Hosted model |
| Complex | Local for non-complex prompts | Hosted model |
| Peak | Local model | Hosted model |
| Cost-constrained | Local model | Hosted model |
| Overload | Local model | Hosted model |

The local model is Qwen2.5-1.5B-Instruct. The hosted path uses the existing Groq integration in `activities/hybrid_pipeline.py`.

## 4. Evaluation: Latency, Cost, and Quality

### Latency

Local inference avoids a network request but may be slow on a CPU, particularly for longer generations. Hosted inference requires a network request but may complete generation faster. Actual latency should be measured in the target environment.

### Cost

Local inference does not require a hosted inference call for each request, although it still uses local computing resources. Hosted inference may incur API usage costs, depending on the provider and account limits. Routing simple prompts locally can reduce hosted API usage.

### Output Quality

The local model is suitable for testing routine requests but may provide less detailed results. The hosted model is intended for more complex prompts. Quality should be evaluated by checking relevance, usefulness, clarity, and whether the response follows user constraints.

## 5. Testing and Limitations

The routing logic can be tested without running model generation by checking the model selected for representative prompts and scenarios. Mock responses can test the routing flow without the latency of real inference.

The routing policy uses simple keyword and prompt-length heuristics rather than a trained complexity classifier. System load and request thresholds are simulated inputs; they are not measurements of live infrastructure unless connected to real monitoring. Latency and output quality comparisons require separate measurements using actual model responses.