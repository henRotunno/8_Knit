"""Measure the local AI recommendation page through Django's request stack."""

import json
from time import perf_counter

from django.core.management.base import BaseCommand
from django.test import Client
from django.test.utils import setup_test_environment, teardown_test_environment
from django.urls import reverse

CASES = (
    (
        "first_hike",
        "My roommates and I are planning our first weekend hike. What should we pack and how should we pick a route?",
    ),
    (
        "running_club",
        "I want to start a beginner-friendly running club for students who have different schedules. How should I organize the first week?",
    ),
    (
        "group_cooking",
        "Four friends want a low-stress cooking night. How can we split jobs and get dinner on the table together?",
    ),
    (
        "book_club",
        "We're starting a small book club for classmates. How should we pick our first book and get everyone talking?",
    ),
    (
        "meet_people",
        "I just moved to Champaign and don't know anyone. What are low-pressure ways to meet people on a Saturday?",
    ),
    (
        "live_information",
        "What time does the ARC close this Saturday and what is the climbing wall fee?",
    ),
    (
        "underspecified_coverage",
        "I need three fun things for a rainy afternoon indoors under $10.",
    ),
    ("unrelated_request", "Which GPU should I buy to train a large language model?"),
    ("blank", "  "),
    ("over_limit", "weekend " * 251),
)


class Command(BaseCommand):
    help = "Run realistic and edge-case prompts through the local activity AI page."

    def handle(self, *args, **options):
        setup_test_environment()
        try:
            client = Client()
            url = reverse("local_llm")
            for case, prompt in CASES:
                started = perf_counter()
                response = client.post(url, {"prompt": prompt})
                elapsed = perf_counter() - started
                context = response.context
                self.stdout.write(json.dumps({
                    "case": case,
                    "seconds": round(elapsed, 3),
                    "http_status": response.status_code,
                    "answer": context.get("response_text", ""),
                    "error": context.get("error", "") or " ".join(context["form"].errors.get("prompt", [])),
                    "chunks": [source["chunk_id"] for source in context.get("sources", [])],
                }))
        finally:
            teardown_test_environment()
