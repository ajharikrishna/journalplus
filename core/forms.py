from django import forms
from .models import JournalTrade, DepositWithdrawal, AccountTransaction

class JournalTradeForm(forms.ModelForm):
    class Meta:
        model = JournalTrade
        exclude = ['user']  # We'll set user from request.user

        widgets = {
            'exit_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        
class DepositWithdrawalForm(forms.ModelForm):
    class Meta:
        model = DepositWithdrawal
        exclude = ['user']  # Again, set user in view

        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'note': forms.Textarea(attrs={'rows': 2}),
        }
        
from django import forms

class TradeImportForm(forms.Form):
    file = forms.FileField(
        label="Upload CSV or Excel File",
        help_text="Accepted formats: .csv, .xlsx"
    )
from django import forms

class DepositWithdrawForm(forms.ModelForm):
    class Meta:
        model = AccountTransaction
        fields = ['transaction_type', 'amount', 'note']
