from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import JournalTrade, AccountTransaction

@receiver(post_save, sender=JournalTrade)
def update_account_balance_from_trade(sender, instance, created, **kwargs):
    if created and instance.trade_return:
        AccountTransaction.objects.create(
            user=instance.user,
            transaction_type='trade',
            amount=instance.trade_return,
            note=f"Auto update from trade: {instance.trade_symbol}"
        )
