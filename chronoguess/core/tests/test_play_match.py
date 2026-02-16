from django.test import TestCase, Client
from unittest.mock import ANY
from chronoguess.core.usecases import new_match
from chronoguess.core.models import Occurrence, Match

class PlayMatchTestCase(TestCase):

    def test_correct_play(self):
        start_match = new_match(lang="en")
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
                "timeline_size_goal": 12,
                "mistakes": [],
                "status": "ongoing",
            }
        )
        self.assertNotEqual(start_match["player_hand"], match_data["match"]["player_hand"])
    
    def test_same_year_earlier_play(self):
        start_match = new_match(lang="en")
        client = Client()

        hand_occurence = Occurrence.objects.get(id=start_match["player_hand"][0]["id"])
        hand_occurence.year = 9999
        hand_occurence.save()


        timeline_occurence = Occurrence.objects.get(id=start_match["timeline"][0]["id"])
        timeline_occurence.year = 9999
        timeline_occurence.save()


        response = client.post(f'/api/match/{start_match["id"]}/', content_type='application/json', data={
            "occurrence_id": start_match["player_hand"][0]["id"],
            "position": 0
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
                "timeline_size_goal": 12,
                "mistakes": [],
                "status": "ongoing",
            }
        )
        self.assertNotEqual(start_match["player_hand"], match_data["match"]["player_hand"])
    

    def test_same_year_later_play(self):
        start_match = new_match(lang="en")
        client = Client()

        hand_occurence = Occurrence.objects.get(id=start_match["player_hand"][0]["id"])
        hand_occurence.year = 9999
        hand_occurence.save()


        timeline_occurence = Occurrence.objects.get(id=start_match["timeline"][0]["id"])
        timeline_occurence.year = 9999
        timeline_occurence.save()


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
                "timeline_size_goal": 12,
                "mistakes": [],
                "status": "ongoing",
            }
        )
        self.assertNotEqual(start_match["player_hand"], match_data["match"]["player_hand"])
    

    def test_wrong_play(self):
        start_match = new_match(lang="en")
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
                "timeline_size_goal": 12,
                "mistakes": [mistake],
                "status": "ongoing",
            }
        )
        self.assertNotEqual(start_match["player_hand"], match_data["match"]["player_hand"])

    def test_lose(self):
        start_match = new_match(lang="en")
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
                "timeline_size_goal": 12,
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
                "timeline_size_goal": 12,
                "mistakes": [first_mistake, second_mistake],
                "status": "lose",
            }
        )


    def test_win(self):
        start_match = new_match(lang="en")
        client = Client()

        for player_hand in range(0, 11):
            match = Match.objects.get(id=start_match["id"])
            occurrence = match.player_hand.first()
            occurrence.year = 9999
            occurrence.save()
            response = client.post(f'/api/match/{start_match["id"]}/', content_type='application/json', data={
                "occurrence_id": occurrence.id,
                "position": 1
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
                "timeline_size_goal": 12,
                "mistakes": [],
                "status": "win",
            }
        )
    
    def test_try_to_play_with_a_card_that_dont_exists_on_player_hands(self):
        start_match = new_match(lang="en")
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
