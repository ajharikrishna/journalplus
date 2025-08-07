from django.db import models
from django.contrib.auth.models import User

class JournalTrade(models.Model):
    TRADE_TYPE_CHOICES = [
        ('buy', 'Buy'),
        ('sell', 'Sell'),
    ]
    SETUP_STRATEGY_CHOICES = [
        ('breakout', 'Breakout'),
        ('reversal', 'Reversal'),
        ('scalping', 'Scalping'),
        ('other', 'Other'),
    ]
    DIRECTION_CHOICES = [
        ('long', 'Long'),
        ('short', 'Short'),
    ]
    OUTCOME_CHOICES = [
        ('win', 'Win'),
        ('loss', 'Loss'),
        ('breakeven', 'Breakeven'),
    ]
    TRADE_CATEGORY_CHOICES = [
        ('intraday', 'Intraday'),
        ('swing', 'Swing'),
        ('fno', 'F&O'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    trade_symbol = models.CharField(max_length=100) 
    trade_type = models.CharField(max_length=10, choices=TRADE_TYPE_CHOICES)
    trade_setup_strategy = models.CharField(max_length=20, choices=SETUP_STRATEGY_CHOICES)
    trade_direction = models.CharField(max_length=10, choices=DIRECTION_CHOICES)
    quantity = models.IntegerField()
    entry_price = models.DecimalField(max_digits=10, decimal_places=2)
    exit_price = models.DecimalField(max_digits=10, decimal_places=2)
    exit_date = models.DateField()
    target_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stop_loss_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fees = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    trade_return = models.DecimalField(max_digits=10, decimal_places=2)
    risk_reward_ratio = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)
    trade_outcome = models.CharField(max_length=10, choices=OUTCOME_CHOICES)
    image = models.ImageField(upload_to='trade_images/', null=True, blank=True)
    trade_category = models.CharField(max_length=10, choices=TRADE_CATEGORY_CHOICES)
    is_swing_trade = models.BooleanField(default=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    # def save(self, *args, **kwargs):
    #     if self.trade_category == 'swing':
    #         self.is_swing_trade == True
    #     else:
    #         self.is_swing_trade == False
    #     super().save(*args, **kwargs)
        
        
    def __str__(self):
        return f"{self.user.username} - {self.trade_type} on {self.exit_date}"


class DepositWithdrawal(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    note = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} ₹{self.amount} on {self.date}"

from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)



#TEST TRANSACTION

class AccountTransaction(models.Model):
    TRANSACTION_TYPE_CHOICES = (
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('trade', 'Trade Result'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.transaction_type} - ₹{self.amount}"
