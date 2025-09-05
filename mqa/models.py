from django.contrib.auth.models import User
from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.
class Quote(models.Model):
    class SourceType(models.TextChoices):
        MOVIE = 'movie', 'Фильм'
        BOOK = 'book', 'Книга'
        SERIES = 'series', 'Сериал'
        GAME = 'game', 'Игра'
        OTHER = 'other', 'Другое'

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    source_name = models.CharField(max_length=255)
    source_type = models.CharField(max_length=20, choices=SourceType.choices, default=SourceType.OTHER)
    quote_content = models.TextField(unique=True)
    weight = models.PositiveIntegerField(default=1, db_index=True)
    views = models.PositiveIntegerField(default=0, db_index=True)
    crete_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-weight",)
        indexes = [
            models.Index(fields=["source_name", "source_type"]),
            models.Index(fields=["weight"]),
            models.Index(fields=["views"]),
        ]

    def __str__(self):
        return self.quote_content

    def clean(self):
        super().clean()
        if self.source_name and self.source_type:
            existing_count = Quote.objects.filter(
                source_name=self.source_name,
                source_type=self.source_type,
            ).exclude(pk=self.pk).count()
            if existing_count >= 3:
                raise ValidationError({
                    "source_name": "Нельзя иметь больше трёх цитат для одного источника.",
                })

    def save(self, *args, **kwargs):
        # Ensure validation (including max-3-per-source) always runs on save
        self.full_clean()
        return super().save(*args, **kwargs)

    @property
    def likes_count(self):
        return self.reactions.filter(value=Reaction.Value.LIKE).count()

    @property
    def dislikes_count(self):
        return self.reactions.filter(value=Reaction.Value.DISLIKE).count()


class Reaction(models.Model):
    class Value(models.IntegerChoices):
        DISLIKE = -1, 'Dislike'
        LIKE = 1, 'Like'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE, related_name="reactions")
    value = models.SmallIntegerField(choices=Value.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "quote")
        indexes = [
            models.Index(fields=["quote", "value"]),
            models.Index(fields=["user", "quote"]),
        ]

    def __str__(self):
        return f"{self.user.username}: {self.get_value_display()} on #{self.quote_id}"
