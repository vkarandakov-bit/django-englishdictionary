from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(
        label='Логин',
        max_length=50,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'поле для ввода имени',
            }
        ),
    )


class AddWordForm(forms.Form):
    russian_word = forms.CharField(
        label='Слово на русском',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    english_word = forms.CharField(
        label='Перевод на английском',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )


class DeleteWordForm(forms.Form):
    word_key = forms.ChoiceField(
        label='Выберите слово для удаления',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    def __init__(self, words, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = []
        for word in words:
            label = (
                f"{word['russian_word']} — {word['english_word']} "
                f"({'Базовое' if word['word_type'] == 'common' else 'Личное'})"
            )
            choices.append((f"{word['word_type']}:{word['id']}", label))
        self.fields['word_key'].choices = choices
