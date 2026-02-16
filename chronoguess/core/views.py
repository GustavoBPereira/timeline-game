import json
from django.http import JsonResponse, HttpResponseNotAllowed
from django.views import View
from django.forms.models import model_to_dict

from chronoguess.core.models import Occurrence

from .usecases import new_match, get_match_by_id, submit_occurence_on_match


class MatchListView(View):
    def get(self, request):
        lang = request.GET.get("lang", "en")
        if lang not in Occurrence.LanguageChoices:
            return JsonResponse({"error": "Invalid language"}, status=400)
        return JsonResponse(new_match(lang), safe=False)


class MatchDetailView(View):
    def get(self, request, match_id):
        match = get_match_by_id(match_id)
        if not match:
            return JsonResponse({"error": "Not found"}, status=404)
        return JsonResponse(match)

    def post(self, request, match_id):
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        match = get_match_by_id(match_id, as_dict=False)
        played_occurence = Occurrence.objects.get(id=payload["occurrence_id"])

        if played_occurence not in match.player_hand.all():
            return JsonResponse({"error": "Occurrence not in player's hand"}, status=400)

        match_result = submit_occurence_on_match(match, played_occurence, position=payload["position"])
        if not match_result:
            return JsonResponse({"error": "Not found"}, status=404)

        return JsonResponse(match_result)

