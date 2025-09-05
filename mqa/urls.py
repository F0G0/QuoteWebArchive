from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home', views.home, name='home'),
    path('sign-up', views.sign_up, name='sign_up'),
    path('create-post', views.create_quote, name='create_quote'),
    path('quotes', views.quotes_list, name='quotes_list'),
    path('my-quotes', views.my_quotes, name='my_quotes'),
    path('quotes/<int:quote_id>/delete', views.delete_quote, name='delete_quote'),
    path('quotes/<int:quote_id>/edit-weight', views.edit_quote_weight, name='edit_quote_weight'),
    path('top', views.top_quotes, name='top_quotes'),
    path('login', views.login_view, name='login'),
]
