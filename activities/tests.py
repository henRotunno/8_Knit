from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, SimpleTestCase, TestCase
from django.urls import reverse

from .local_llm import MAX_PROMPT_LENGTH
from .models import Activities


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


class MostFavoritedActivitiesTests(TestCase):
    def setUp(self):
        self.url = reverse("most_favorited_activities")

    def test_public_endpoint_counts_favorites_and_orders_ties_by_name(self):
        first_user = get_user_model().objects.create_user(username="first")
        second_user = get_user_model().objects.create_user(username="second")
        chess = Activities.objects.create(activity_name="Chess")
        hiking = Activities.objects.create(activity_name="Hiking")
        art = Activities.objects.create(activity_name="Art")
        Activities.objects.create(activity_name="Board games")
        chess.favorited_by.add(first_user)
        hiking.favorited_by.add(first_user, second_user)
        art.favorited_by.add(second_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertEqual(response.json(), [
            {"activity_name": "Hiking", "favorite_count": 2},
            {"activity_name": "Art", "favorite_count": 1},
            {"activity_name": "Chess", "favorite_count": 1},
            {"activity_name": "Board games", "favorite_count": 0},
        ])

    def test_empty_database_returns_an_empty_list(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_counts_follow_favorite_changes_without_counting_duplicate_adds(self):
        user = get_user_model().objects.create_user(username="reader")
        activity = Activities.objects.create(activity_name="Reading")
        self.assertEqual(self.client.get(self.url).json(), [
            {"activity_name": "Reading", "favorite_count": 0},
        ])

        activity.favorited_by.add(user)
        activity.favorited_by.add(user)
        self.assertEqual(self.client.get(self.url).json(), [
            {"activity_name": "Reading", "favorite_count": 1},
        ])

        activity.favorited_by.remove(user)
        self.assertEqual(self.client.get(self.url).json(), [
            {"activity_name": "Reading", "favorite_count": 0},
        ])

    def test_dashboard_keeps_existing_charts_and_adds_favorites_widget(self):
        response = self.client.get(reverse("vega-charts"))

        self.assertTemplateUsed(response, "vega_charts.html")
        self.assertContains(response, 'id="activity-category-chart"')
        self.assertContains(response, 'id="user-friends-chart"')
        self.assertContains(response, 'id="most-favorited-activities-chart"')
        self.assertContains(response, "User Behavior")
        self.assertContains(response, "Most Favorited Activities")
        self.assertContains(response, self.url)
