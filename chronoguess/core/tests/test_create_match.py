from django.test import TestCase, Client
from chronoguess.core.usecases import new_match

class CreateMatchTestCase(TestCase):

    def test_success(self):
        client = Client()
    
        response = client.get(f'/api/match/')
        self.assertEqual(response.status_code, 200)

        match_data = response.json()
        self.assertDictEqual(match_data, {
            "id": match_data["id"],
            "player_hand": match_data["player_hand"],
            "timeline": match_data["timeline"],
            "remaining_life": 3,
            "timeline_size_goal": 12,
            "mistakes": [],
            "status": "ongoing",
        })
        self.assertEqual(len(match_data["player_hand"]), 1)
        self.assertEqual(len(match_data["timeline"]), 1)
        self.assertIsNone(match_data["player_hand"][0]["year"])
    
    def test_invalid_language(self):
        client = Client()
        response = client.get(f'/api/match/?lang=invalid')
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(response.json(), {"error": "Invalid language"})
