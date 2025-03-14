from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import (
    Profile, PredefinedAction, PointTransaction, VirtualGift,
    GiftTransaction, Challenge, ChallengeParticipation,
    Memory, SurpriseMessage, Badge, UserBadge
)
from django.db.models import Sum

@login_required
def home(request):
    user_profile = Profile.objects.get(user=request.user)
    recent_points = PointTransaction.objects.filter(
        receiver=user_profile
    ).order_by('-created_at')[:5]
    recent_gifts = GiftTransaction.objects.filter(
        receiver=user_profile
    ).order_by('-created_at')[:5]
    active_challenges = ChallengeParticipation.objects.filter(
        profile=user_profile,
        status='active'
    )
    badges = UserBadge.objects.filter(profile=user_profile)
    
    context = {
        'profile': user_profile,
        'recent_points': recent_points,
        'recent_gifts': recent_gifts,
        'active_challenges': active_challenges,
        'badges': badges,
    }
    return render(request, 'love_points/home.html', context)

@login_required
def profile(request):
    user_profile = Profile.objects.get(user=request.user)
    
    # دریافت تراکنش‌های امتیازات معمولی
    received_points_transactions = PointTransaction.objects.filter(
        receiver=user_profile
    ).order_by('-created_at')
    
    sent_points_transactions = PointTransaction.objects.filter(
        giver=user_profile
    ).order_by('-created_at')
    
    # دریافت تراکنش‌های هدایا
    received_gifts_transactions = GiftTransaction.objects.filter(
        receiver=user_profile
    ).order_by('-created_at')
    
    sent_gifts_transactions = GiftTransaction.objects.filter(
        sender=user_profile
    ).order_by('-created_at')
    
    # محاسبه مجموع امتیازات معمولی
    total_received_points = received_points_transactions.aggregate(
        total=Sum('points')
    )['total'] or 0
    
    total_sent_points = sent_points_transactions.aggregate(
        total=Sum('points')
    )['total'] or 0
    
    # محاسبه مجموع امتیازات هدایا
    total_received_gift_points = received_gifts_transactions.aggregate(
        total=Sum('gift__points_cost')
    )['total'] or 0
    
    total_sent_gift_points = sent_gifts_transactions.aggregate(
        total=Sum('gift__points_cost')
    )['total'] or 0
    
    # محاسبه مجموع کل
    total_received = total_received_points + total_received_gift_points
    total_sent = total_sent_points + total_sent_gift_points
    
    # دریافت نشان‌ها
    badges = UserBadge.objects.filter(profile=user_profile)
    
    context = {
        'profile': user_profile,
        'received_points_transactions': received_points_transactions,
        'sent_points_transactions': sent_points_transactions,
        'received_gifts_transactions': received_gifts_transactions,
        'sent_gifts_transactions': sent_gifts_transactions,
        'total_received': total_received,
        'total_sent': total_sent,
        'total_received_points': total_received_points,
        'total_sent_points': total_sent_points,
        'total_received_gift_points': total_received_gift_points,
        'total_sent_gift_points': total_sent_gift_points,
        'badges': badges,
    }
    return render(request, 'love_points/profile.html', context)

@login_required
def give_points(request):
    if request.method == 'POST':
        action_id = request.POST.get('action')
        custom_points = request.POST.get('custom_points')
        custom_description = request.POST.get('custom_description')
        
        giver_profile = Profile.objects.get(user=request.user)
        receiver_profile = giver_profile.partner
        
        if not receiver_profile:
            messages.error(request, 'شما هنوز پارتنری انتخاب نکرده‌اید.')
            return redirect('love_points:home')
        
        # Handle predefined action
        if action_id:
            action = get_object_or_404(PredefinedAction, id=action_id)
            points = action.points
        # Handle custom points
        elif custom_points:
            try:
                points = int(custom_points)
                if points < 1 or points > 100:
                    messages.error(request, 'امتیاز باید بین 1 تا 100 باشد.')
                    return redirect('love_points:give_points')
                action = None
            except ValueError:
                messages.error(request, 'لطفاً یک عدد معتبر وارد کنید.')
                return redirect('love_points:give_points')
        else:
            messages.error(request, 'لطفاً یک اقدام را انتخاب کنید یا امتیاز دلخواه وارد کنید.')
            return redirect('love_points:give_points')
            
        # ایجاد تراکنش امتیاز
        PointTransaction.objects.create(
            giver=giver_profile,
            receiver=receiver_profile,
            points=points,
            action=action,
            custom_description=custom_description
        )
        
        # افزایش امتیاز دریافت‌کننده
        receiver_profile.points += points
        receiver_profile.save()
        
        messages.success(request, f'{points} امتیاز با موفقیت به {receiver_profile.user.username} داده شد.')
        return redirect('love_points:home')
        
    predefined_actions = PredefinedAction.objects.all()
    return render(request, 'love_points/give_points.html', {'actions': predefined_actions})

@login_required
def gift_shop(request):
    gifts = VirtualGift.objects.all()
    user_profile = Profile.objects.get(user=request.user)
    return render(request, 'love_points/gift_shop.html', {
        'gifts': gifts,
        'user_points': user_profile.points
    })

@login_required
def send_gift(request, gift_id):
    if request.method == 'POST':
        gift = get_object_or_404(VirtualGift, id=gift_id)
        sender_profile = Profile.objects.get(user=request.user)
        
        if sender_profile.points < gift.points_cost:
            messages.error(request, 'امتیاز کافی برای خرید این هدیه ندارید.')
            return redirect('love_points:gift_shop')
            
        message = request.POST.get('message')
        image = request.FILES.get('image')
        
        GiftTransaction.objects.create(
            sender=sender_profile,
            receiver=sender_profile.partner,
            gift=gift,
            message=message,
            image=image
        )
        
        sender_profile.points -= gift.points_cost
        sender_profile.save()
        
        messages.success(request, 'هدیه با موفقیت ارسال شد.')
        return redirect('love_points:home')
        
    gift = get_object_or_404(VirtualGift, id=gift_id)
    return render(request, 'love_points/send_gift.html', {'gift': gift})

@login_required
def challenges(request):
    user_profile = Profile.objects.get(user=request.user)
    available_challenges = Challenge.objects.all()
    
    # Get active challenges for both user and partner
    active_challenges = ChallengeParticipation.objects.filter(
        profile=user_profile,
        status='active'
    )
    
    # Get partner's active challenges that need confirmation
    partner_challenges = ChallengeParticipation.objects.filter(
        profile=user_profile.partner,
        status='active',
        partner_confirmation=False
    ) if user_profile.partner else []
    
    completed_challenges = ChallengeParticipation.objects.filter(
        profile=user_profile,
        status='completed'
    )
    
    context = {
        'available_challenges': available_challenges,
        'active_challenges': active_challenges,
        'partner_challenges': partner_challenges,
        'completed_challenges': completed_challenges,
    }
    return render(request, 'love_points/challenges.html', context)

@login_required
def join_challenge(request, challenge_id):
    challenge = get_object_or_404(Challenge, id=challenge_id)
    user_profile = Profile.objects.get(user=request.user)
    
    if ChallengeParticipation.objects.filter(
        profile=user_profile,
        challenge=challenge,
        status='active'
    ).exists():
        messages.error(request, 'شما قبلاً در این چالش شرکت کرده‌اید.')
        return redirect('love_points:challenges')
        
    participation = ChallengeParticipation.objects.create(
        profile=user_profile,
        challenge=challenge,
        end_date=timezone.now() + timezone.timedelta(days=challenge.duration_days)
    )
    
    messages.success(request, f'شما با موفقیت در چالش {challenge.title} شرکت کردید.')
    return redirect('love_points:challenges')

@login_required
def confirm_challenge(request, participation_id):
    participation = get_object_or_404(ChallengeParticipation, id=participation_id)
    user_profile = Profile.objects.get(user=request.user)
    
    if user_profile != participation.profile.partner:
        messages.error(request, 'شما اجازه تأیید این چالش را ندارید.')
        return redirect('love_points:challenges')
        
    participation.partner_confirmation = True
    participation.status = 'completed'
    participation.save()
    
    # اعطای امتیاز به کاربر
    participation.profile.points += participation.challenge.points_reward
    participation.profile.save()
    
    messages.success(request, f'چالش با موفقیت تأیید شد و {participation.challenge.points_reward} امتیاز به {participation.profile.user.username} داده شد.')
    return redirect('love_points:challenges')

@login_required
def memories(request):
    user_profile = Profile.objects.get(user=request.user)
    
    # Get memories from both the user and their partner
    memories_list = Memory.objects.filter(
        profile__in=[user_profile, user_profile.partner]
    ).order_by('-created_at')
    
    return render(request, 'love_points/memories.html', {'memories': memories_list})

@login_required
def add_memory(request):
    if request.method == 'POST':
        user_profile = Profile.objects.get(user=request.user)
        title = request.POST.get('title')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        
        Memory.objects.create(
            profile=user_profile,
            title=title,
            description=description,
            image=image
        )
        
        messages.success(request, 'خاطره جدید با موفقیت ثبت شد.')
        return redirect('love_points:memories')
        
    return render(request, 'love_points/add_memory.html')

@login_required
def surprise_messages(request):
    user_profile = Profile.objects.get(user=request.user)
    now = timezone.localtime(timezone.now())
    
    # Get received messages that are ready to be opened
    received_messages = SurpriseMessage.objects.filter(
        receiver=user_profile,
        open_date__lte=now
    ).order_by('-created_at')
    
    # Get all sent messages
    sent_messages = SurpriseMessage.objects.filter(
        sender=user_profile
    ).order_by('-created_at')
    
    # Get locked messages (messages that can't be opened yet)
    locked_messages = SurpriseMessage.objects.filter(
        receiver=user_profile,
        open_date__gt=now
    ).order_by('open_date')
    
    # Mark messages as opened if they haven't been opened yet
    for message in received_messages:
        if not message.is_opened:
            message.is_opened = True
            message.save()
    
    context = {
        'received_messages': received_messages,
        'sent_messages': sent_messages,
        'locked_messages': locked_messages,
        'now': now,
    }
    return render(request, 'love_points/surprise_messages.html', context)

@login_required
def send_surprise(request):
    if request.method == 'POST':
        sender_profile = Profile.objects.get(user=request.user)
        message = request.POST.get('message')
        open_date = request.POST.get('open_date')
        
        if not sender_profile.partner:
            messages.error(request, 'شما هنوز پارتنری انتخاب نکرده‌اید.')
            return redirect('love_points:surprise_messages')
            
        if not message:
            messages.error(request, 'لطفاً متن پیام را وارد کنید.')
            return redirect('love_points:send_surprise')
            
        if not open_date:
            messages.error(request, 'لطفاً تاریخ باز شدن پیام را مشخص کنید.')
            return redirect('love_points:send_surprise')
            
        try:
            # Convert string datetime to Python datetime
            open_date = timezone.datetime.strptime(open_date, '%Y-%m-%dT%H:%M')
            # Make it timezone aware
            open_date = timezone.make_aware(open_date)
            
            if open_date < timezone.now():
                messages.error(request, 'تاریخ باز شدن پیام نمی‌تواند در گذشته باشد.')
                return redirect('love_points:send_surprise')
                
            surprise_message = SurpriseMessage.objects.create(
                sender=sender_profile,
                receiver=sender_profile.partner,
                message=message,
                open_date=open_date
            )
            
            messages.success(request, 'پیام سورپرایز با موفقیت ارسال شد.')
            return redirect('love_points:surprise_message_detail', message_id=surprise_message.id)
            
        except ValueError:
            messages.error(request, 'فرمت تاریخ وارد شده صحیح نیست.')
            return redirect('love_points:send_surprise')
        
    context = {
        'min_date': timezone.now()
    }
    return render(request, 'love_points/send_surprise.html', context)

@login_required
def surprise_message_detail(request, message_id):
    message = get_object_or_404(SurpriseMessage, id=message_id)
    user_profile = request.user.profile
    now = timezone.now()
    
    # Check if user has permission to view this message
    if message.sender != user_profile and message.receiver != user_profile:
        messages.error(request, 'شما اجازه مشاهده این پیام را ندارید.')
        return redirect('love_points:surprise_messages')
    
    # Make sure both times are timezone aware for comparison
    message_open_date = timezone.localtime(message.open_date)
    current_time = timezone.localtime(now)
    
    # If receiver is viewing and message is ready to be opened
    if message.receiver == user_profile and not message.is_opened and message_open_date <= current_time:
        message.is_opened = True
        message.save()
    
    # Check if the message can be viewed
    can_view = message.sender == user_profile or (message.receiver == user_profile and message_open_date <= current_time)
    
    if not can_view and message.receiver == user_profile:
        messages.warning(request, f'این پیام در تاریخ {message_open_date|date:"Y/m/d H:i"} قابل مشاهده خواهد بود.')
    
    context = {
        'message': message,
        'now': current_time,
        'can_view': can_view
    }
    return render(request, 'love_points/surprise_message_detail.html', context)

@login_required
def edit_memory(request, memory_id):
    memory = get_object_or_404(Memory, id=memory_id, profile=request.user.profile)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        
        memory.title = title
        memory.description = description
        if image:
            memory.image = image
        memory.save()
        
        messages.success(request, 'خاطره با موفقیت ویرایش شد.')
        return redirect('love_points:memories')
        
    return render(request, 'love_points/edit_memory.html', {'memory': memory})

@login_required
def delete_memory(request, memory_id):
    memory = get_object_or_404(Memory, id=memory_id, profile=request.user.profile)
    memory.delete()
    messages.success(request, 'خاطره با موفقیت حذف شد.')
    return redirect('love_points:memories')

@login_required
def received_gifts(request):
    user_profile = request.user.profile
    received_gifts = GiftTransaction.objects.filter(receiver=user_profile).order_by('-created_at')
    
    context = {
        'received_gifts': received_gifts,
    }
    return render(request, 'love_points/received_gifts.html', context)

@login_required
def gift_detail(request, gift_id):
    user_profile = request.user.profile
    gift = get_object_or_404(GiftTransaction, id=gift_id)
    
    # Check if the user is either the sender or receiver
    if gift.sender != user_profile and gift.receiver != user_profile:
        messages.error(request, 'شما اجازه دسترسی به این هدیه را ندارید.')
        return redirect('love_points:received_gifts')
    
    context = {
        'gift': gift,
    }
    return render(request, 'love_points/gift_detail.html', context)
