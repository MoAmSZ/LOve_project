from django.contrib import admin
from .models import (
    Profile, PredefinedAction, PointTransaction, VirtualGift,
    GiftTransaction, Challenge, ChallengeParticipation,
    Memory, SurpriseMessage, Badge, UserBadge
)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'points', 'level', 'partner', 'created_at')
    search_fields = ('user__username',)

@admin.register(PredefinedAction)
class PredefinedActionAdmin(admin.ModelAdmin):
    list_display = ('name', 'points')
    search_fields = ('name',)

@admin.register(PointTransaction)
class PointTransactionAdmin(admin.ModelAdmin):
    list_display = ('giver', 'receiver', 'points', 'action', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('giver__user__username', 'receiver__user__username')

@admin.register(VirtualGift)
class VirtualGiftAdmin(admin.ModelAdmin):
    list_display = ('name', 'points_cost')
    search_fields = ('name',)

@admin.register(GiftTransaction)
class GiftTransactionAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'gift', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('sender__user__username', 'receiver__user__username')

@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('title', 'points_reward', 'duration_days')
    search_fields = ('title',)

@admin.register(ChallengeParticipation)
class ChallengeParticipationAdmin(admin.ModelAdmin):
    list_display = ('profile', 'challenge', 'status', 'start_date', 'end_date')
    list_filter = ('status', 'start_date')
    search_fields = ('profile__user__username',)

@admin.register(Memory)
class MemoryAdmin(admin.ModelAdmin):
    list_display = ('profile', 'title', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('profile__user__username', 'title')

@admin.register(SurpriseMessage)
class SurpriseMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'open_date', 'is_opened', 'created_at')
    list_filter = ('is_opened', 'created_at')
    search_fields = ('sender__user__username', 'receiver__user__username')

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'required_points')
    search_fields = ('name',)

@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ('profile', 'badge', 'earned_at')
    list_filter = ('earned_at',)
    search_fields = ('profile__user__username', 'badge__name')
