from django.test import TestCase, Client
from chronoguess.core.usecases import new_match

class GetMatchTestCase(TestCase):

    def test_success(self):
        match = new_match(lang="en")
        client = Client()
    
        response = client.get(f'/api/match/{match["id"]}/')
        self.assertEqual(response.status_code, 200)

        match_data = response.json()
        self.assertEqual(match, match_data)

    
    def test_not_found(self):
        client = Client()
        response = client.get('/api/match/1/')
        self.assertEqual(response.status_code, 404)
    

