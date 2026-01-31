from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Occurrence(BaseModel):
    title = models.CharField(max_length=255)
    summary = models.TextField()
    photo_url = models.URLField(blank=True, null=True)
    year = models.IntegerField()

    def as_dict(self, hide_year=False):
        return {
            'id': self.id,
            'title': self.title,
            'summary': self.summary,
            'photo_url': self.photo_url,
            'year': self.year if not hide_year else None,
        }

    def __str__(self):
        return f'{self.title} - {self.year}'


class Game(BaseModel):
    deck = models.ManyToManyField('Occurrence', related_name='game_deck')
    starting_hand = models.ForeignKey('Occurrence', on_delete=models.CASCADE, related_name='starting_hand_card')
    starting_timeline = models.ForeignKey('Occurrence', on_delete=models.CASCADE, related_name='starting_board_card')

class Match(BaseModel):
    
    class StatusChoices(models.TextChoices):
        ONGOING = 'ongoing', 'Ongoing'
        WIN = 'win', 'Win'
        LOSE = 'lose', 'Lose'

    game = models.ForeignKey('Game', on_delete=models.CASCADE, related_name='match')
    timeline = models.ManyToManyField('Occurrence', related_name='timeline_occurrences')
    player_hand = models.ManyToManyField('Occurrence', related_name='player_hand')
    deck = models.ManyToManyField('Occurrence', related_name='match_deck')
    
    remaining_life = models.IntegerField(default=3)
    status = models.CharField(
        max_length=20,
        choices=StatusChoices,
        default=StatusChoices.ONGOING
    )

    def as_dict(self):
        return {
            'id': self.id,
            'player_hand': [occurrence.as_dict(hide_year=True) for occurrence in self.player_hand.all()],
            'timeline': [occurrence.as_dict() for occurrence in self.timeline.all()],
            'remaining_deck': self.deck.count(),
            'remaining_life': self.remaining_life,
            'status': self.status,
        }