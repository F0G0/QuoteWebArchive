from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Quote

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = [
            'source_name',
            'source_type',
            'quote_content',
            'weight',
        ]
        labels = {
            'source_name': 'Источник',
            'source_type': 'Тип источника',
            'quote_content': 'Цитата',
            'weight': 'Вес',
        }
        help_texts = {
            'source_name': 'Название фильма/книги/игры и т.п.',
            'source_type': 'Выберите тип источника.',
            'quote_content': 'Текст новой цитаты. Дубликаты запрещены.',
            'weight': 'Чем выше вес, тем выше шанс показа (мин. 1).',
        }
        widgets = {
            'source_name': forms.TextInput(),
            'source_type': forms.Select(),
            'quote_content': forms.Textarea(attrs={'rows': 4}),
            'weight': forms.NumberInput(attrs={'min': 1}),
        }

    def clean_weight(self):
        weight = self.cleaned_data.get('weight')
        if weight is None or weight < 1:
            raise forms.ValidationError('Вес должен быть не меньше 1.')
        return weight

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

