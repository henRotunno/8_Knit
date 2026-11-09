from unittest.mock import patch

from django.test import Client, SimpleTestCase
from django.urls import reverse

from .local_llm import MAX_PROMPT_LENGTH


class ActivityAIViewTests(SimpleTestCase):
    def setUp(self):
        self.url = reverse("local_llm")

    @patch("activities.local_llm.retrieve_activity_context")
    def test_navigation_and_invalid_inputs_do_not_load_models(self, retrieve):
        self.assertContains(self.client.get(reverse("home")), self.url)
        self.assertContains(self.client.get(self.url), "csrfmiddlewaretoken")
        self.assertFormError(
            self.client.post(self.url, {"prompt": "  "}).context["form"],
            "prompt",
            "Please describe the activity you’re looking for.",
        )
        response = self.client.post(self.url, {"prompt": "x" * (MAX_PROMPT_LENGTH + 1)})
        self.assertTrue(response.context["form"].has_error("prompt", "max_length"))
        retrieve.assert_not_called()
        self.assertEqual(Client(enforce_csrf_checks=True).post(self.url, {"prompt": "Hike"}).status_code, 403)

    @patch("activities.local_llm.get_generator")
    @patch("activities.local_llm.retrieve_activity_context")
    def test_answer_uses_retrieved_context_and_renders_as_text(self, retrieve, get_generator):
        retrieve.return_value = [
            {"text": "Bring water.", "topic_label": "Hiking camping", "chunk_id": "hybrid_013"},
        ]
        generate = get_generator.return_value.create_chat_completion
        generate.return_value = (
            {"choices": [{"delta": {"content": text}}]}
            for text in ["<b>Bring water</b>"]
        )
        response = self.client.post(self.url, {"prompt": " First hike "})
        retrieve.assert_called_once_with("First hike")
        messages = generate.call_args.kwargs["messages"]
        self.assertIn("Bring water.", messages[1]["content"])
        self.assertContains(response, "&lt;b&gt;Bring water&lt;/b&gt;")
        self.assertContains(response, "hybrid_013")

    @patch("activities.local_llm.get_generator")
    @patch("activities.local_llm.retrieve_activity_context", return_value=[])
    def test_no_context_skips_generation(self, retrieve, get_generator):
        response = self.client.post(self.url, {"prompt": "GPU shopping"})
        self.assertContains(response, "activity guides don’t cover this request")
        get_generator.assert_not_called()

    @patch("activities.local_llm.get_generator")
    @patch("activities.local_llm.retrieve_activity_context", return_value=[{"text": "Bring water."}])
    def test_empty_output_and_loading_failure_show_friendly_errors(self, retrieve, get_generator):
        get_generator.return_value.create_chat_completion.return_value = (
            {"choices": [{"delta": {"content": text}}]} for text in [" "]
        )
        with self.assertLogs("activities.local_llm", level="ERROR"):
            response = self.client.post(self.url, {"prompt": "First hike"})
        self.assertContains(response, "couldn’t generate suggestions")

        retrieve.side_effect = RuntimeError("internal model loading error")
        with self.assertLogs("activities.local_llm", level="ERROR"):
            response = self.client.post(self.url, {"prompt": "First hike"})
        self.assertContains(response, "couldn’t generate suggestions")
        self.assertNotContains(response, "internal model loading error")

    @patch("activities.local_llm.get_generator")
    @patch("activities.local_llm.retrieve_activity_context", return_value=[{"text": "Bring water."}])
    @patch("activities.local_llm.perf_counter", side_effect=[0, 46])
    def test_timeout_discards_partial_answer(self, clock, retrieve, get_generator):
        get_generator.return_value.create_chat_completion.return_value = (
            {"choices": [{"delta": {"content": text}}]} for text in ["Partial advice"]
        )
        response = self.client.post(self.url, {"prompt": "First hike"})
        self.assertContains(response, "took too long")
        self.assertNotContains(response, "Partial advice")
