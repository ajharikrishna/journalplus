from django.contrib import admin
from .models import JournalTrade, DepositWithdrawal, UserProfile, AccountTransaction

@admin.register(JournalTrade)
class JournalTradeAdmin(admin.ModelAdmin):
    list_display = ['user', 'trade_type', 'exit_date', 'trade_return', 'trade_outcome', 'trade_category']
    list_filter = ['trade_outcome', 'exit_date', 'trade_category']
    search_fields = ['user__username', 'notes']

@admin.register(DepositWithdrawal)
class DepositWithdrawalAdmin(admin.ModelAdmin):
    list_display = ['user', 'transaction_type', 'amount', 'date']
    list_filter = ['transaction_type', 'date']
    search_fields = ['user__username', 'note']

# @admin.register(UserProfile)
# class UserProfileAdmin(admin.ModelAdmin):
#     list_display = ['user']

@admin.register(AccountTransaction)
class AccountTransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'transaction_type', 'amount',]
