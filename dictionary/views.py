from django.contrib import messages
from django.shortcuts import redirect, render
from .forms import AddWordForm, DeleteWordForm, LoginForm
from .models import CommonWord, Learner, LearningStat, UserWord
from .services import (
    add_personal_word,
    build_question,
    delete_word,
    get_statistics,
    get_user_words,
    get_user_words_count,
    login_user,
    seed_common_words,
    update_stats,
)


def _require_user(request):
    user_id = request.session.get('user_id')
    username = request.session.get('username')
    if not user_id:
        return None, None
    return user_id, username


def home(request):
    seed_common_words()

    user_id, username = _require_user(request)
    if user_id:
        return redirect('study')

    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username']
        request.session['user_id'] = login_user(username)
        request.session['username'] = username
        request.session.pop('current_question', None)
        request.session.pop('feedback', None)
        return redirect('study')

    return render(request, 'dictionary/home.html', {'form': form})


def logout_view(request):
    request.session.flush()
    return redirect('home')


def study(request):
    seed_common_words()
    user_id, username = _require_user(request)
    if not user_id:
        return redirect('home')

    words = get_user_words(user_id)
    feedback = request.session.pop('feedback', None)

    if len(words) < 4:
        return render(
            request,
            'dictionary/study.html',
            {
                'username': username,
                'not_enough_words': True,
                'words_count': len(words),
                'missing_count': 4 - len(words),
            },
        )

    if request.method == 'POST':
        action = request.POST.get('action')
        question = request.session.get('current_question')

        if action == 'answer' and question:
            selected = request.POST.get('option', '').lower()
            is_correct = selected == question['english_word'].lower()
            update_stats(user_id, question['id'], question['word_type'], is_correct)
            if is_correct:
                request.session['feedback'] = ('success', 'Абсолютно верно!')
            else:
                request.session['feedback'] = ('error', 'Неправильно. Попробуйте снова!')
            return redirect('study')

        if action == 'next':
            request.session.pop('current_question', None)
            request.session.pop('feedback', None)
            return redirect('study')

    question = request.session.get('current_question')
    if not question:
        question = build_question(words)
        request.session['current_question'] = question

    return render(
        request,
        'dictionary/study.html',
        {
            'username': username,
            'question': question,
            'feedback': feedback,
        },
    )


def add_word(request):
    seed_common_words()
    user_id, username = _require_user(request)
    if not user_id:
        return redirect('home')

    total_count = None
    form = AddWordForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        ru_word = form.cleaned_data['russian_word']
        eng_word = form.cleaned_data['english_word']
        if add_personal_word(user_id, ru_word, eng_word):
            total_count = get_user_words_count(user_id)
            messages.success(request, f'Слово «{ru_word}» успешно сохранено!')
            messages.info(
                request,
                f'Всего слов в вашей программе обучения теперь: {total_count}',
            )
            form = AddWordForm()
        else:
            messages.warning(request, 'Такое слово уже есть в вашем словаре.')

    return render(
        request,
        'dictionary/add_word.html',
        {
            'username': username,
            'form': form,
            'total_count': total_count,
        },
    )


def delete_word_view(request):
    seed_common_words()
    user_id, username = _require_user(request)
    if not user_id:
        return redirect('home')

    words = get_user_words(user_id)
    form = None

    if not words:
        return render(
            request,
            'dictionary/delete_word.html',
            {'username': username, 'words': words, 'form': form},
        )

    form = DeleteWordForm(words, request.POST or None)
    if request.method == 'POST' and form.is_valid():
        word_type, word_id = form.cleaned_data['word_key'].split(':')
        delete_word(user_id, int(word_id), word_type)
        request.session.pop('current_question', None)
        messages.success(request, 'Слово успешно удалено из вашего профиля!')
        return redirect('delete_word')

    return render(
        request,
        'dictionary/delete_word.html',
        {
            'username': username,
            'words': words,
            'form': form,
        },
    )


def statistics(request):
    seed_common_words()
    user_id, username = _require_user(request)
    if not user_id:
        return redirect('home')

    stats = get_statistics(user_id)
    accuracy = 0
    if stats['attempts']:
        accuracy = (stats['correct'] / stats['attempts']) * 100

    return render(
        request,
        'dictionary/statistics.html',
        {
            'username': username,
            'stats': stats,
            'accuracy': accuracy,
        },
    )


def schema(request):
    seed_common_words()
    user_id, username = _require_user(request)
    if not user_id:
        return redirect('home')

    tables = [
        {
            'name': 'users',
            'model': Learner,
            'color': 'table-primary',
        },
        {
            'name': 'common_words',
            'model': CommonWord,
            'color': 'table-success',
        },
        {
            'name': 'user_words',
            'model': UserWord,
            'color': 'table-warning',
        },
        {
            'name': 'learning_stats',
            'model': LearningStat,
            'color': 'table-danger',
        },
    ]

    schema_tables = []
    for table in tables:
        fields = []
        for field in table['model']._meta.get_fields():
            if getattr(field, 'auto_created', False) and not field.concrete:
                continue
            fields.append(
                {
                    'name': field.name,
                    'type': field.get_internal_type(),
                    'primary_key': getattr(field, 'primary_key', False),
                }
            )
        schema_tables.append(
            {
                'name': table['name'],
                'color': table['color'],
                'fields': fields,
            }
        )

    relations = [
        ('user_words.user_id', 'users.id'),
        ('learning_stats.user_id', 'users.id'),
        ('learning_stats.word_id', 'common_words.id (logical)'),
    ]

    return render(
        request,
        'dictionary/schema.html',
        {
            'username': username,
            'schema_tables': schema_tables,
            'relations': relations,
        },
    )
