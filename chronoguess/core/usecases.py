from .models import Match, Game, Occurrence
from django.core.exceptions import ObjectDoesNotExist


def new_match(lang: str):
    selected_occurrences = list(Occurrence.objects.filter(language=lang).order_by('?')[:15])
    starting_hand = selected_occurrences[0]
    starting_timeline = selected_occurrences[1]
    game = Game.objects.create(
        starting_hand=starting_hand,
        starting_timeline=starting_timeline,
    )
    deck = selected_occurrences[2:]
    game.deck.set(deck)
    match = Match.objects.create(game=game)
    match.player_hand.set([starting_hand])
    match.timeline.set([starting_timeline])
    match.deck.set(deck)

    return match.as_dict()


def get_match_by_id(match_id, as_dict=True):
    match = Match.objects.filter(id=match_id).first()
    if not match:
        return None
    return match.as_dict() if as_dict else match

def submit_occurence_on_match(match, played_occurence, position: int):

    timeline = match.timeline.order_by('year')
    
    correct_submition = False
    if position == 0:
        correct_submition = timeline[0].year >= played_occurence.year
    elif position < len(timeline):
        correct_submition = timeline[position - 1].year <= played_occurence.year <= timeline[position].year
    elif position == len(timeline):
        correct_submition = timeline.last().year <= played_occurence.year
    else:
        raise ValueError("Invalid position")
    
    if correct_submition:
        match.timeline.add(played_occurence)
    else:
        match.remaining_life -= 1
        match.mistakes.add(played_occurence)
        if match.remaining_life <= 0:
            match.status = Match.StatusChoices.LOSE
        
    
    match.player_hand.remove(played_occurence)
    drawed_card = match.deck.first()
    if drawed_card:
        match.player_hand.add(drawed_card)
        match.deck.remove(drawed_card)
    match.save()

    if match.deck.count() == 0 and match.player_hand.count() == 0:
        match.status = Match.StatusChoices.WIN
        match.save()

    return {
        "status": "correct" if correct_submition else "incorrect",
        "match": match.as_dict()
    }
