GitHub repository for Knit

The Weavers (Team 8) will be creating an app called
“Knit” in response to the changing dynamics observed in this
college town. People come and go, and individuals with whom one
once shared hobbies may no longer be in the same town after
graduating. There are times when an individual would like to find
someone to join them in an activity, such as running, playing board
games, or practicing a dance, but they may not know where to find
people who are also interested in participating. Currently,
invitations to participate in group activities are often scattered
across different platforms, such as Facebook, Reddit, and group
chats. Therefore, the Weavers would like to create an app that
brings people with similar interests together, allows them to
participate in activities, and helps them build new friendships.

## API

The project includes an Activities API endpoint that returns activity data in JSON format.

- `/api/activities/` returns all activities using `JsonResponse`.
- `/api/activities/?q=run` filters activities using the `q` query parameter.
- `/api/activities-http/` returns the same activity data using a standard `HttpResponse` for comparison.

The JSON API returns activity IDs and activity names from the Activities model.

## Local setup

Use 64-bit Python 3.12. In Windows PowerShell, run these commands from the
repository root. An existing `.venv` and `.env` are reused:

```powershell
if (-not (Test-Path .venv\Scripts\python.exe)) { py -3.12 -m venv .venv }
.\.venv\Scripts\python.exe -m pip install -r requirements.txt --only-binary=llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Set `SECRET_KEY` in `.env` to a local development secret before starting
Django. Keep any existing environment values. The explicit interpreter path
avoids PowerShell activation-policy issues. Then run:

```powershell
$env:DJANGO_SETTINGS_MODULE = "Knit_Application.settings.development"
$env:HF_HOME = Join-Path (Get-Location) ".cache\huggingface"
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

The existing dependency versions in `requirements.txt` are retained. A9 adds
`llama-cpp-python` for GGUF inference and an explicit `huggingface-hub` dependency
for model downloads. The Hub version is compatible with the existing
Transformers requirement. The upstream
[CPU wheel index](https://abetlen.github.io/llama-cpp-python/whl/cpu/llama-cpp-python/)
provides a Windows x64 Python 3.12 wheel for the pinned llama-cpp-python version;
`--only-binary` prevents an unexpected C++ build. A source installation instead
requires a C/C++ toolchain, such as Visual Studio or MinGW on Windows. See the
[llama-cpp-python installation instructions](https://llama-cpp-python.readthedocs.io/en/latest/).

On Linux or macOS, create and activate a Python 3.12 virtual environment, use
`python -m pip install -r requirements.txt`, and set
`DJANGO_SETTINGS_MODULE=Knit_Application.settings.development` before the Django
commands above. If no matching wheel is available, llama-cpp-python builds from
source using the platform's C/C++ toolchain. Preserve an existing `.env` when
copying `.env.example`.

The repository currently contains an A7 notebook directory named
`P1-A7: Multi-Model AI Systems (Part 2)`. Its colon is invalid in Windows paths.
A Windows checkout must exclude that directory using Git sparse checkout;
this keeps the team's notebook files tracked and does not affect Django.

Open [AI Activity Suggestions](http://127.0.0.1:8000/local-llm/) from the main
navigation and enter a weekend activity request. Try "How should my roommates
and I prepare for our first weekend hike?" The page is accessible without an account.

The first supported request downloads BGE-small and the official Qwen2.5-1.5B
Q4_K_M GGUF from Hugging Face (about 1.25 GB total), builds the in-memory search
index, and loads both models on CPU. Subsequent requests reuse the loaded models
in the same process. Allow extra time and memory for the first request. Model
files live in the Hugging Face cache; the PowerShell setup above relocates it
inside the ignored `.cache/` directory. Set `HF_HOME` before starting Django
when using another cache location. Model weights and caches must stay out of Git.
The recommendation page uses no API key. The separate, authenticated
`/hybrid-ai/` text-refinement page requires `GROQ_API_KEY` if used.

Run the web regression tests with
`.\.venv\Scripts\python.exe manage.py test activities`. Run the real-model
evaluation through the Django page with
`.\.venv\Scripts\python.exe manage.py evaluate_activity_ai`.
See [README_AI.md](README_AI.md) for the design and prepared evaluation results.
