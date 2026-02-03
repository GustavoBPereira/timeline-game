from django.test import TestCase, Client
from unittest.mock import ANY
from timeline.core.usecases import new_match
from timeline.core.models import Occurrence, Match

class PlayMatchTestCase(TestCase):

    def test_correct_play(self):
        start_match = new_match()
        client = Client()

        occurence = Occurrence.objects.get(id=start_match["player_hand"][0]["id"])
        occurence.year = 9999
        occurence.save()

        response = client.post(f'/api/match/{start_match["id"]}/', content_type='application/json', data={
            "occurrence_id": start_match["player_hand"][0]["id"],
            "position": 1
        })
        self.assertEqual(response.status_code, 200)

        match_data = response.json()
        self.assertNotEqual(start_match, match_data["match"])
        self.assertEqual(match_data["status"], "correct")

        self.assertDictEqual(
            match_data["match"],
            {
                "id": match_data["match"]["id"],
                "player_hand": ANY,
                "timeline": match_data["match"]["timeline"],
                "remaining_life": 3,
                "remaining_deck": start_match["remaining_deck"] - 1,
                "mistakes": [],
                "status": "ongoing",
            }
        )
        self.assertNotEqual(start_match["player_hand"], match_data["match"]["player_hand"])
    
    def test_wrong_play(self):
        start_match = new_match()
        client = Client()

        occurence = Occurrence.objects.get(id=start_match["player_hand"][0]["id"])
        occurence.year = 9999
        occurence.save()

        response = client.post(f'/api/match/{start_match["id"]}/', content_type='application/json', data={
            "occurrence_id": start_match["player_hand"][0]["id"],
            "position": 0
        })
        self.assertEqual(response.status_code, 200)

        match_data = response.json()
        self.assertNotEqual(start_match, match_data["match"])
        self.assertEqual(match_data["status"], "incorrect")
        mistake = Occurrence.objects.get(id=start_match["player_hand"][0]["id"]).as_dict()

        self.assertDictEqual(
            match_data["match"],
            {
                "id": match_data["match"]["id"],
                "player_hand": ANY,
                "timeline": match_data["match"]["timeline"],
                "remaining_life": 2,
                "remaining_deck": start_match["remaining_deck"] - 1,
                "mistakes": [mistake],
                "status": "ongoing",
            }
        )
        self.assertNotEqual(start_match["player_hand"], match_data["match"]["player_hand"])

    def test_lose(self):
        start_match = new_match()
        client = Client()

        occurence = Occurrence.objects.get(id=start_match["player_hand"][0]["id"])
        occurence.year = 9999
        occurence.save()

        match = Match.objects.get(id=start_match["id"])
        match.remaining_life = 2
        match.save()

        response = client.post(f'/api/match/{start_match["id"]}/', content_type='application/json', data={
            "occurrence_id": start_match["player_hand"][0]["id"],
            "position": 0
        })
        self.assertEqual(response.status_code, 200)

        match_data = response.json()
        self.assertNotEqual(start_match, match_data["match"])
        self.assertEqual(match_data["status"], "incorrect")

        first_mistake = Occurrence.objects.get(id=start_match["player_hand"][0]["id"]).as_dict()

        self.assertDictEqual(
            match_data["match"],
            {
                "id": match_data["match"]["id"],
                "player_hand": ANY,
                "timeline": match_data["match"]["timeline"],
                "remaining_life": 1,
                "remaining_deck": start_match["remaining_deck"] - 1,
                "mistakes": [first_mistake],
                "status": "ongoing",
            }
        )

        occurence = Occurrence.objects.get(id=match_data["match"]["player_hand"][0]["id"])
        occurence.year = 9999
        occurence.save()
        second_mistake = Occurrence.objects.get(id=match_data["match"]["player_hand"][0]["id"]).as_dict()
        response = client.post(f'/api/match/{start_match["id"]}/', content_type='application/json', data={
            "occurrence_id": match_data["match"]["player_hand"][0]["id"],
            "position": 0
        })

        match_data = response.json()
        self.assertNotEqual(start_match, match_data["match"])
        self.assertEqual(match_data["status"], "incorrect")

        self.assertDictEqual(
            match_data["match"],
            {
                "id": match_data["match"]["id"],
                "player_hand": ANY,
                "timeline": match_data["match"]["timeline"],
                "remaining_life": 0,
                "remaining_deck": start_match["remaining_deck"] - 2,
                "mistakes": [first_mistake, second_mistake],
                "status": "lose",
            }
        )


    def test_win(self):
        start_match = new_match()
        client = Client()

        match = Match.objects.get(id=start_match["id"])
        match.deck.clear()
        match.player_hand.clear()
        for occurrence_data in start_match["timeline"]:
            occurrence = Occurrence.objects.get(id=occurrence_data["id"])
            match.player_hand.add(occurrence)
        match.save()

        for occurrence_data in start_match["timeline"]:
            occurrence = Occurrence.objects.get(id=occurrence_data["id"])
            occurrence.year = 9999
            occurrence.save()

            response = client.post(f'/api/match/{start_match["id"]}/', content_type='application/json', data={
                "occurrence_id": occurrence.id,
                "position": len(match.timeline.all())
            })
            self.assertEqual(response.status_code, 200)

            match_data = response.json()

        self.assertEqual(match_data["status"], "correct")

        self.assertDictEqual(
            match_data["match"],
            {
                "id": match_data["match"]["id"],
                "player_hand": [],
                "timeline": match_data["match"]["timeline"],
                "remaining_life": 3,
                "remaining_deck": 0,
                "mistakes": [],
                "status": "win",
            }
        )
    
    def test_try_to_play_with_a_card_that_dont_exists_on_player_hands(self):
        start_match = new_match()
        client = Client()

        occurrence = Occurrence.objects.create(
            title="Invalid Card",
            summary="This card is not in player's hand",
            year=2000
        )
        occurrence.save()

        response = client.post(f'/api/match/{start_match["id"]}/', content_type='application/json', data={
            "occurrence_id": occurrence.id,
            "position": 1
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Occurrence not in player's hand"})
