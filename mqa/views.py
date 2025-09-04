from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from mqa.forms import RegisterForm, QuoteForm
from mqa.models import Quote, Reaction
from django.db.models import Sum, F
import random
from django.contrib import messages
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth import authenticate, login, logout
@login_required(login_url='/login')
def home(request):
    if request.method == 'POST':
        action = request.POST.get('reaction')
        quote_id = request.POST.get('quote_id')
        if action in {'like', 'dislike'} and quote_id:
            try:
                quote = Quote.objects.get(pk=quote_id)
            except Quote.DoesNotExist:
                messages.error(request, 'Цитата не найдена.')
            else:
                desired_value = Reaction.Value.LIKE if action == 'like' else Reaction.Value.DISLIKE
                existing = Reaction.objects.filter(user=request.user, quote=quote).first()
                if existing and existing.value == desired_value:
                    existing.delete()
                    messages.success(request, 'Реакция удалена.')
                else:
                    Reaction.objects.update_or_create(
                        user=request.user,
                        quote=quote,
                        defaults={'value': desired_value},
                    )
                    messages.success(request, 'Реакция сохранена.')
        return redirect('home')

    weighted_quote = None
    quotes_qs = Quote.objects.all()
    total_weight = quotes_qs.aggregate(total=Sum('weight')).get('total') or 0
    if total_weight > 0:
        pick = random.randint(1, total_weight)
        cumulative = 0
        for quote in quotes_qs:
            cumulative += quote.weight
            if pick <= cumulative:
                weighted_quote = quote
                break
    if weighted_quote is not None:
        Quote.objects.filter(pk=weighted_quote.pk).update(views=F('views') + 1)
        try:
            weighted_quote.views = (weighted_quote.views or 0) + 1
        except Exception:
            pass
        user_reaction = Reaction.objects.filter(user=request.user, quote=weighted_quote).first()
    else:
        user_reaction = None
    return render(request, 'mqa/home.html', {'q': weighted_quote, 'user_reaction': user_reaction})


@login_required(login_url='/login')
def quotes_list(request):
    quotes = (
        Quote.objects.select_related('author')
        .order_by('-weight', '-views', '-update_time', '-id')
    )
    return render(request, 'mqa/quotes_list.html', {"quotes": quotes})

def sign_up(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/home')
    else:
        form = RegisterForm()
    return render(request, 'registration/sign_up.html', {'form': form})


@login_required(login_url='/login')
def create_quote(request):
    if request.method == 'POST':
        form = QuoteForm(request.POST)
        if form.is_valid():
            quote = form.save(commit=False)
            quote.author = request.user
            try:
                quote.save()
            except DjangoValidationError as e:
                if hasattr(e, 'message_dict'):
                    for field_name, error_list in e.message_dict.items():
                        for error_message in error_list:
                            if field_name == '__all__':
                                form.add_error(None, error_message)
                            else:
                                form.add_error(field_name, error_message)
                else:
                    for error_message in e.messages:
                        form.add_error(None, error_message)
                messages.error(request, 'Цитата не сохранена из-за ограничений. Исправьте ошибки ниже.')
            else:
                messages.success(request, 'Цитата успешно создана.')
                return redirect('/home')
    else:
        form = QuoteForm()
    return render(request, 'mqa/create_post.html',{"form": form})
