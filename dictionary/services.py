import random

from django.db.models import Sum

from .models import CommonWord, Learner, LearningStat, UserWord

BASE_WORDS = [
    ('красный', 'red'),
    ('синий', 'blue'),
    ('зеленый', 'green'),
    ('желтый', 'yellow'),
    ('белый', 'white'),
    ('я', 'i'),
    ('ты / вы', 'you'),
    ('он', 'he'),
    ('она', 'she'),
    ('мы', 'we'),
]


def seed_common_words():
    if CommonWord.objects.exists():
        return
    CommonWord.objects.bulk_create(
        [CommonWord(russian_word=ru, english_word=eng) for ru, eng in BASE_WORDS]
    )


def login_user(username):
    learner, _ = Learner.objects.get_or_create(username=username.strip())
    return learner.id


def get_user_words(user_id):
    deleted_common_ids = LearningStat.objects.filter(
        user_id=user_id,
        word_type=LearningStat.WordType.COMMON,
        is_deleted=True,
    ).values_list('word_id', flat=True)

    words = []
    for word in CommonWord.objects.exclude(id__in=deleted_common_ids):
        words.append(
            {
                'id': word.id,
                'russian_word': word.russian_word,
                'english_word': word.english_word,
                'word_type': LearningStat.WordType.COMMON,
            }
        )

    for word in UserWord.objects.filter(user_id=user_id):
        words.append(
            {
                'id': word.id,
                'russian_word': word.russian_word,
                'english_word': word.english_word,
                'word_type': LearningStat.WordType.PERSONAL,
            }
        )

    return words


def add_personal_word(user_id, russian_word, english_word):
    ru_clean = russian_word.strip().lower()
    eng_clean = english_word.strip().lower()

    exists = UserWord.objects.filter(
        user_id=user_id,
        russian_word__iexact=ru_clean,
        english_word__iexact=eng_clean,
    ).exists()
    if exists:
        return False

    UserWord.objects.create(
        user_id=user_id,
        russian_word=russian_word.strip(),
        english_word=english_word.strip(),
    )
    return True


def delete_word(user_id, word_id, word_type):
    if word_type == LearningStat.WordType.PERSONAL:
        UserWord.objects.filter(id=word_id, user_id=user_id).delete()
        return

    LearningStat.objects.update_or_create(
        user_id=user_id,
        word_id=word_id,
        word_type=LearningStat.WordType.COMMON,
        defaults={'is_deleted': True},
    )


def update_stats(user_id, word_id, word_type, is_correct):
    stat, _ = LearningStat.objects.get_or_create(
        user_id=user_id,
        word_id=word_id,
        word_type=word_type,
        defaults={'correct_answers': 0, 'total_attempts': 0},
    )
    stat.total_attempts += 1
    if is_correct:
        stat.correct_answers += 1
    stat.is_deleted = False
    stat.save()


def get_statistics(user_id):
    stats = LearningStat.objects.filter(
        user_id=user_id,
        is_deleted=False,
    ).aggregate(
        total_words=Sum('id'),
        attempts=Sum('total_attempts'),
        correct=Sum('correct_answers'),
    )

    total_words = LearningStat.objects.filter(
        user_id=user_id,
        is_deleted=False,
    ).count()

    return {
        'total_words': total_words,
        'attempts': stats['attempts'] or 0,
        'correct': stats['correct'] or 0,
    }


def get_user_words_count(user_id):
    deleted_common_ids = LearningStat.objects.filter(
        user_id=user_id,
        word_type=LearningStat.WordType.COMMON,
        is_deleted=True,
    ).values_list('word_id', flat=True)

    common_count = CommonWord.objects.exclude(id__in=deleted_common_ids).count()
    personal_count = UserWord.objects.filter(user_id=user_id).count()
    return common_count + personal_count


def generate_options(correct_word, all_words):
    options = {correct_word.lower()}
    pool = [
        word['english_word'].lower()
        for word in all_words
        if word['english_word'].lower() != correct_word.lower()
    ]

    if len(pool) >= 3:
        options.update(random.sample(pool, 3))
    else:
        options.update(pool)

    while len(options) < 4 and len(pool) > len(options) - 1:
        for item in pool:
            options.add(item)
            if len(options) >= 4:
                break

    result = list(options)[:4]
    random.shuffle(result)
    return result


def build_question(words):
    target = random.choice(words)
    options = generate_options(target['english_word'], words)
    return {
        'id': target['id'],
        'word_type': target['word_type'],
        'russian_word': target['russian_word'],
        'english_word': target['english_word'],
        'options': options,
    }
