from django.urls import path
from . import views

app_name = 'love_points'

urlpatterns = [
    path('', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('give-points/', views.give_points, name='give_points'),
    path('gift-shop/', views.gift_shop, name='gift_shop'),
    path('send-gift/<int:gift_id>/', views.send_gift, name='send_gift'),
    path('received-gifts/', views.received_gifts, name='received_gifts'),
    path('gift-detail/<int:gift_id>/', views.gift_detail, name='gift_detail'),
    path('challenges/', views.challenges, name='challenges'),
    path('join-challenge/<int:challenge_id>/', views.join_challenge, name='join_challenge'),
    path('confirm-challenge/<int:participation_id>/', views.confirm_challenge, name='confirm_challenge'),
    path('memories/', views.memories, name='memories'),
    path('add-memory/', views.add_memory, name='add_memory'),
    path('edit-memory/<int:memory_id>/', views.edit_memory, name='edit_memory'),
    path('delete-memory/<int:memory_id>/', views.delete_memory, name='delete_memory'),
    path('surprise-messages/', views.surprise_messages, name='surprise_messages'),
    path('send-surprise/', views.send_surprise, name='send_surprise'),
    path('surprise-message/<int:message_id>/', views.surprise_message_detail, name='surprise_message_detail'),
] 