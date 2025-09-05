from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from .models import Quote

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    #Почему-то не давало поменять через  labels
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Имя пользователя'
        self.fields['email'].label = 'Электронная почта'
        self.fields['password1'].label = 'Пароль'
        self.fields['password2'].label = 'Повтор пароля'

        self.fields['username'].help_text = ''
        self.fields['email'].help_text = ''
        self.fields['password1'].help_text = 'Минимум 8 символов. Не используйте слишком простой пароль.'
        self.fields['password2'].help_text = 'Повторите пароль для подтверждения.'


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set Russian labels
        self.fields['username'].label = 'Имя пользователя'
        self.fields['password'].label = 'Пароль'
        
        # Set placeholders
        self.fields['username'].widget.attrs.setdefault('placeholder', 'Имя пользователя')
        self.fields['password'].widget.attrs.setdefault('placeholder', 'Пароль')


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


class QuoteWeightForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = ['weight']
        labels = {'weight': 'Вес'}
        help_texts = {'weight': 'Чем выше вес, тем выше шанс показа (мин. 1).'}
        widgets = {'weight': forms.NumberInput(attrs={'min': 1})}

    def clean_weight(self):
        weight = self.cleaned_data.get('weight')
        if weight is None or weight < 1:
            raise forms.ValidationError('Вес должен быть не меньше 1.')
        return weight

