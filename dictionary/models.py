from django.db import models


class Learner(models.Model):
    username = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.username


class CommonWord(models.Model):
    russian_word = models.CharField(max_length=100)
    english_word = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'common_words'

    def __str__(self):
        return f'{self.russian_word} — {self.english_word}'


class UserWord(models.Model):
    user = models.ForeignKey(
        Learner,
        on_delete=models.CASCADE,
        related_name='personal_words',
    )
    russian_word = models.CharField(max_length=100)
    english_word = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_words'

    def __str__(self):
        return f'{self.russian_word} — {self.english_word}'


class LearningStat(models.Model):
    class WordType(models.TextChoices):
        COMMON = 'common', 'Common'
        PERSONAL = 'personal', 'Personal'

    user = models.ForeignKey(
        Learner,
        on_delete=models.CASCADE,
        related_name='learning_stats',
    )
    word_id = models.IntegerField()
    word_type = models.CharField(max_length=10, choices=WordType.choices)
    correct_answers = models.IntegerField(default=0)
    total_attempts = models.IntegerField(default=0)
    is_deleted = models.BooleanField(default=False)
    last_reviewed = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'learning_stats'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'word_id', 'word_type'],
                name='unique_user_word_type',
            ),
        ]
