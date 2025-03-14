from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    partner = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class PredefinedAction(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    points = models.IntegerField(validators=[MinValueValidator(1)])
    
    def __str__(self):
        return self.name

class PointTransaction(models.Model):
    giver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='points_given')
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='points_received')
    points = models.IntegerField(validators=[MinValueValidator(1)])
    action = models.ForeignKey(PredefinedAction, on_delete=models.SET_NULL, null=True, blank=True)
    custom_description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.giver.user.username} gave {self.points} points to {self.receiver.user.username}"

class VirtualGift(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='gifts/')
    points_cost = models.IntegerField(validators=[MinValueValidator(1)])
    
    def __str__(self):
        return self.name

class GiftTransaction(models.Model):
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='gifts_sent')
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='gifts_received')
    gift = models.ForeignKey(VirtualGift, on_delete=models.CASCADE)
    message = models.TextField()
    image = models.ImageField(upload_to='memories/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.user.username} sent {self.gift.name} to {self.receiver.user.username}"

class Challenge(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    points_reward = models.IntegerField(validators=[MinValueValidator(1)])
    duration_days = models.IntegerField(validators=[MinValueValidator(1)])
    
    def __str__(self):
        return self.title

class ChallengeParticipation(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ]
    
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    partner_confirmation = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.profile.user.username}'s {self.challenge.title} Challenge"

class Memory(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='memories/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.profile.user.username}'s Memory: {self.title}"

class SurpriseMessage(models.Model):
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='surprises_sent')
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='surprises_received')
    message = models.TextField()
    open_date = models.DateTimeField()
    is_opened = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Surprise from {self.sender.user.username} to {self.receiver.user.username}"

class Badge(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='badges/')
    required_points = models.IntegerField(validators=[MinValueValidator(1)])
    
    def __str__(self):
        return self.name

class UserBadge(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.profile.user.username} earned {self.badge.name}"
