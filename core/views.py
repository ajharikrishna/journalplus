

# Create your views here.
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from django.contrib.auth.decorators import login_required
from .models import JournalTrade
from .forms import JournalTradeForm

from django.shortcuts import render
from django.db.models import Avg, Count, Sum, Q
from core.models import JournalTrade
from datetime import datetime, timedelta
from collections import defaultdict
from django.db.models.functions import TruncDate


# @login_required
# def dashboard_view(request):
#     trades = JournalTrade.objects.filter(user=request.user)
    

#     # Handle P&L Over Time
#     daily_returns = defaultdict(list)
   
#     for trade in trades.exclude(exit_date__isnull=True).exclude(trade_return__isnull=True):
#         date_only = trade.exit_date
#         daily_returns[date_only].append(trade.trade_return)

#     labels = []
#     data = []

#     for date, returns in sorted(daily_returns.items()):
#         labels.append(date.strftime("%b %d"))
#         data.append(round(sum(returns) / len(returns), 2))

#     # Handle Trade Outcome pie
#     outcome_data = {
#         "Win": trades.filter(trade_outcome="Win").count(),
#         "Loss": trades.filter(trade_outcome="Loss").count(),
#         "Break Even": trades.filter(trade_outcome="Break Even").count(),
#     }
#     print("labes" , labels, data, outcome_data)
#     return render(request, "dashboard.html", {
#         "labels": labels,
#         "data": data,
#         "outcome_data": outcome_data,
#     })

@login_required
def dashboard_view(request):
    trades = JournalTrade.objects.filter(user=request.user)

    # --- Filters ---
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    strategy = request.GET.get("strategy")
    trade_type = request.GET.get("trade_type")

    if start_date:
        trades = trades.filter(exit_date__gte=start_date)
    if end_date:
        trades = trades.filter(exit_date__lte=end_date)
    if strategy:
        trades = trades.filter(trade_setup_strategy=strategy)
    if trade_type:
        trades = trades.filter(trade_category=trade_type)

    # --- Stats ---
    total_trades = trades.count()
    wins = trades.filter(trade_outcome="win").count()
    losses = trades.filter(trade_outcome="loss").count()
    breakeven = trades.filter(trade_outcome="break_even").count()

    win_percentage = round((wins / total_trades) * 100, 2) if total_trades > 0 else 0

    avg_return = trades.aggregate(avg=Avg("trade_return"))["avg"]
    avg_return = round(avg_return, 2) if avg_return else 0

    # # --- P&L Chart Data ---
    # pl_data = (
    # trades.exclude(exit_date__isnull=True)
    # .exclude(trade_return__isnull=True)
    # .values("exit_date")
    # .annotate(total_pl=Avg("trade_return"))
    # .order_by("exit_date")
    # )

    # labels = []
    # data = []

    # for entry in pl_data:
    #     date = entry["exit_date"]
    #     if date:
    #         labels.append(date.strftime("%b %d"))
    #         data.append(round(entry["total_pl"], 2))

     # P&L over time (monthly or daily sample)
    date_wise_pl = trades.order_by("exit_date").values("exit_date").annotate(total=Sum("trade_return"))

    labels = [item["exit_date"].strftime("%b %d") for item in date_wise_pl]
    data = [float(item["total"]) for item in date_wise_pl]

    # Group trades manually by date
    # daily_returns = defaultdict(list)

    # for trade in trades.exclude(exit_date__isnull=True).exclude(trade_return__isnull=True):
    #     date_only = trade.exit_date.date()  # Convert datetime to date
    #     daily_returns[date_only].append(trade.trade_return)

    # # Calculate daily averages
    # labels = []
    # data = []

    # for date, returns in sorted(daily_returns.items()):
    #     labels.append(date.strftime("%b %d"))
    #     data.append(round(sum(returns) / len(returns), 2))

    
    
    
    
    # --- Outcome Pie Data ---
    outcome_data = {
        "win": wins,
        "loss": losses,
        "breakeven": breakeven,
    }

    # --- Strategy Dropdown Values ---
    strategies = JournalTrade.objects.values_list("trade_setup_strategy", flat=True).distinct()

    context = {
        "total_trades": total_trades,
        "win_percentage": win_percentage,
        "avg_return": avg_return,
        "labels": labels,
        "data": data,
        "outcome_data": outcome_data,
        "strategies": strategies,
    }
    return render(request, "dashboard.html", context)

def register_view(request):
    if request.method == "POST":
        username = request.POST['username']
        email    = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('register')
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password1)
        login(request, user)
        return redirect('home')
    
    return render(request, 'register.html')

def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')
    
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')


def home_view(request):
    return render(request, 'home.html')

# @login_required
# def trade_list_view(request):
#     return render(request, 'trades.html')

from django.db.models import Sum, Count

@login_required
def trade_list(request):
    trades = JournalTrade.objects.filter(user=request.user)
    trade_type = request.GET.get('type')
    if trade_type:
        trades = trades.filter(trade_category=trade_type)

    total_pl = trades.aggregate(Sum('trade_return'))['trade_return__sum'] or 0
    wins = trades.filter(trade_outcome='win').count()
    losses = trades.filter(trade_outcome='loss').count()
    breakevens = trades.filter(trade_outcome='breakeven').count()

    context = {
        'trades': trades.order_by('-exit_date'),
        'total_pl': total_pl,
        'wins': wins,
        'losses': losses,
        'breakevens': breakevens,
    }
    return render(request, 'trades.html', context)

# @login_required
# def add_trade_view(request):
#     messages.success(request, "Trade added successfully.")
#     return render(request, 'trade_form.html')

@login_required
def add_trade(request):
    if request.method == 'POST':
        form = JournalTradeForm(request.POST, request.FILES)
        if form.is_valid():
            trade = form.save(commit=False)
            trade.user = request.user
            trade.save()
            messages.success(request, "Trade added successfully.")
            return redirect('trade_list')  # Update this name if needed
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = JournalTradeForm()

    return render(request, 'trade_form.html', {'form': form, 'action': 'Add'})

@login_required
def trade_detail(request, pk):
    trade = get_object_or_404(JournalTrade, pk=pk)
    return render(request, 'trade_detail.html', {'trade': trade})


@login_required
def edit_trade(request, pk):
    trade = get_object_or_404(JournalTrade, pk=pk, user=request.user)
    if request.method == 'POST':
        form = JournalTradeForm(request.POST, request.FILES, instance=trade)
        if form.is_valid():
            form.save()
            messages.success(request, "Trade updated successfully.")
            return redirect('trade_list')
    else:
        form = JournalTradeForm(instance=trade)
        print(form)
    return render(request, 'trade_form.html', {'form': form, 'editing': True})

@login_required
def delete_trade(request, pk):
    trade = get_object_or_404(JournalTrade, pk=pk, user=request.user)
    trade.delete()
    messages.success(request, "Trade deleted successfully.")
    return redirect('trade_list')



@login_required
def deposit_view(request):
    return render(request, 'deposits.html')

from .forms import DepositWithdrawalForm
from .models import DepositWithdrawal
from django.contrib import messages
from django.shortcuts import redirect

@login_required
def add_deposit_withdrawal(request):
    if request.method == 'POST':
        form = DepositWithdrawalForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            messages.success(request, "Transaction recorded.")
            return redirect('deposit_list')  # or wherever you want to redirect
    else:
        form = DepositWithdrawalForm()
    deposits = DepositWithdrawal.objects.filter(user=request.user).order_by('-date')
    return render(request, 'deposits.html', {'form': form, 'deposits': deposits})

@login_required
def deposit_list(request):
    deposits = DepositWithdrawal.objects.filter(user=request.user).order_by('-date')
    return render(request, 'deposit_list.html', {'deposits': deposits})


@login_required
def summary_view(request):
    return render(request, 'summary.html')


from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash


@login_required
def profile_view(request):
    form = PasswordChangeForm(request.user)
    return render(request, 'profile.html', {'form': form})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password updated successfully.')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'profile.html', {'form': form})


# def export_reports(request):
#     return render(request, 'export_reports.html')



### THIS IS FOR EXPORT PDF & EXCEL ### WILL DO LATER ####

# import datetime
# from django.http import HttpResponse
# import pandas as pd
# from .models import Trade  # use your actual Trade model
# from django.shortcuts import render
# from django.db.models import Q

# def export_reports(request):
#     trades = Trade.objects.all()

#     # Get filters from GET
#     start_date = request.GET.get('start_date')
#     end_date = request.GET.get('end_date')
#     category = request.GET.get('category')
#     export_type = request.GET.get('export')

#     # Filter
#     if start_date:
#         trades = trades.filter(exit_date__gte=start_date)
#     if end_date:
#         trades = trades.filter(exit_date__lte=end_date)
#     if category:
#         trades = trades.filter(trade_category=category)

#     # Export Logic
#     if export_type == 'excel':
#         df = pd.DataFrame(trades.values())
#         response = HttpResponse(content_type='application/vnd.ms-excel')
#         response['Content-Disposition'] = 'attachment; filename=trades.xlsx'
#         df.to_excel(response, index=False)
#         return response

#     elif export_type == 'pdf':
#         # simple plain text PDF using reportlab
#         from reportlab.pdfgen import canvas
#         response = HttpResponse(content_type='application/pdf')
#         response['Content-Disposition'] = 'attachment; filename=trades.pdf'
#         p = canvas.Canvas(response)
#         y = 800
#         p.drawString(100, y, "Trade Report")
#         for trade in trades:
#             y -= 20
#             p.drawString(100, y, f"{trade.exit_date} | {trade.trade_category} | {trade.trade_return}")
#         p.showPage()
#         p.save()
#         return response

#     context = {
#         'trades': trades,
#     }
#     return render(request, 'export_reports.html', context)


##TEST CALENDAR1

import calendar
from datetime import date, datetime

@login_required
def trade_calendar(request):
    today = date.today()
    year = int(request.GET.get("year", today.year))
    month = int(request.GET.get("month", today.month))

    month_calendar = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]

    # Get all trades for the given month
    trades = JournalTrade.objects.filter(
        user=request.user,
        exit_date__year=year,
        exit_date__month=month
    )

    # Group trades by day
    trades_by_day = {}
    for trade in trades:
        day = trade.exit_date.day
        trades_by_day.setdefault(day, []).append(trade)

    context = {
        "year": year,
        "month": month,
        "month_name": month_name,
        "month_calendar": month_calendar,
        "trades_by_day": trades_by_day,
        "week_days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], 
    }
    return render(request, 'trade_calendar1.html',context)


##end TEST CALENDAR1


##############START CALENDR!

# from datetime import date, timedelta
# import calendar
# from collections import defaultdict
# from django.shortcuts import render
# from .models import JournalTrade

# def trade_calendar(request):
#     today = date.today()
#     start = today.replace(day=1)
#     _, last_day = calendar.monthrange(today.year, today.month)
    
#     # Generate days matrix for the calendar
#     days_matrix = []
#     week = []
#     start_weekday = start.weekday()  # Monday=0
#     for _ in range(start_weekday):
#         week.append(None)
#     for day in range(1, last_day + 1):
#         d = date(today.year, today.month, day)
#         week.append(d)
#         if len(week) == 7:
#             days_matrix.append(week)
#             week = []
#     if week:
#         while len(week) < 7:
#             week.append(None)
#         days_matrix.append(week)

#     # Group trades by day
#     trades = JournalTrade.objects.filter(user=request.user, exit_date__month=today.month)
#     trades_by_day = defaultdict(list)
#     for t in trades:
#         trades_by_day[t.exit_date].append(t)

#     context = {
#         'today': today,
#         'calendar_weeks': days_matrix,
#         'trades_by_day': trades_by_day,
#     }
#     return render(request, 'trade_calendar2.html', context)



################# end

from django.shortcuts import render
from core.models import JournalTrade
from django.db.models import Sum, Count, Q
from datetime import datetime

@login_required
def export_reports(request):
    trades = JournalTrade.objects.filter(user=request.user)

    # Filters
    trade_type = request.GET.get('trade_type')
    outcome = request.GET.get('trade_outcome')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    strategy = request.GET.get("strategy")
    notes = request.GET.get("notes")


    if trade_type:
        trades = trades.filter(trade_category=trade_type)
    if outcome:
        trades = trades.filter(trade_outcome=outcome)
    if start_date:
        trades = trades.filter(exit_date__gte=start_date)
    if end_date:
        trades = trades.filter(exit_date__lte=end_date)
    if strategy:
        trades = trades.filter(trade_setup_strategy__icontains=strategy)
    if notes:
        trades = trades.filter(notes__icontains=notes)

    # Summary
    total_trades = trades.count()
    total_profit = trades.aggregate(Sum("trade_return"))["trade_return__sum"] or 0
    wins = trades.filter(trade_outcome="win").count()
    win_ratio = round((wins / total_trades) * 100, 2) if total_trades > 0 else 0

    context = {
        "trades": trades,
        "total_trades": total_trades,
        "total_profit": total_profit,
        "win_ratio": win_ratio,
        "selected_trade_type": trade_type,
        "selected_outcome": outcome,
        "start_date": start_date,
        "end_date": end_date,
        "wins":wins
    }
    return render(request, "reports.html", context)


import pandas as pd
from django.http import HttpResponse
from .models import JournalTrade

@login_required
def export_excel(request):
    trades = JournalTrade.objects.all()
    df = pd.DataFrame.from_records(trades.values())
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="trades.xlsx"'
    df.to_excel(response, index=False)
    return response

# core/views.py
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from .models import JournalTrade
import datetime
import io
import os


@login_required
def export_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="trade_report.pdf"'

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # --- Title
    title = Paragraph("📊 Trade Report", styles["Title"])
    elements.append(title)

    # --- Generated Date
    now = datetime.now().strftime('%d %b %Y, %I:%M %p')
    date_paragraph = Paragraph(f"Generated on: {now}", styles["Normal"])
    elements.append(date_paragraph)
    elements.append(Spacer(1, 12))

    # --- Optional: Logo (if exists)
    logo_path = os.path.join("static", "logo.png")  # Replace with your logo path
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=80, height=40)
        elements.append(logo)
        elements.append(Spacer(1, 12))

    # --- Fetch Trades
    trades = JournalTrade.objects.filter(user=request.user).order_by('-exit_date')

    # --- Table Headers
    data = [[
        "Date", "Type", "Symbol", "Qty", "Entry", "Exit",
        "Return (%)", "Strategy", "Outcome"
    ]]

    # --- Table Body
    total_return = 0
    win_count = loss_count = breakeven_count = 0

    for trade in trades:
        trade_return = trade.trade_return or 0
        total_return += trade_return

        # Count Outcomes
        outcome = trade.trade_outcome.lower()
        if "win" in outcome:
            win_count += 1
        elif "loss" in outcome:
            loss_count += 1
        elif "break" in outcome:
            breakeven_count += 1

        data.append([
            trade.exit_date.strftime('%d-%b-%Y') if trade.exit_date else "",
            trade.trade_type,
            getattr(trade, "trade_symbol", ""),  # fallback if symbol not in model
            trade.quantity,
            f"{trade.entry_price:.2f}",
            f"{trade.exit_price:.2f}",
            f"{trade_return:.2f}",
            trade.trade_setup_strategy,
            trade.trade_outcome
        ])

    # --- Create Table
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#222222")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey])
    ]))
    elements.append(table)
    elements.append(Spacer(1, 16))

    # --- Summary Section
    summary = [
        f"📌 Total Trades: {len(trades)}",
        f"✅ Wins: {win_count}",
        f"❌ Losses: {loss_count}",
        f"➖ Break Even: {breakeven_count}",
        f"💰 Total Return: {total_return:.2f}%",
    ]
    for item in summary:
        elements.append(Paragraph(item, styles["Normal"]))

    # --- Build and Return
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


#Import Trades
import csv
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import JournalTrade
from .forms import JournalTradeForm


@login_required
def import_trades(request):
    if request.method == "POST" and request.FILES.get("import_file"):
        file = request.FILES["import_file"]
        file_ext = file.name.split('.')[-1]

        try:
            if file_ext == "csv":
                df = pd.read_csv(file)
            elif file_ext in ["xls", "xlsx"]:
                df = pd.read_excel(file)
            else:
                messages.error(request, "Unsupported file format. Please upload a CSV or Excel file.")
                return redirect("import_trades")
            
            # Validate columns
            required_columns = {"trade_type", "trade_setup_strategy", "trade_direction", "quantity", "entry_price", "exit_price", "exit_date", "target_price", "stop_loss_price", "fees", "trade_return", "risk_reward_ratio", "notes", "trade_outcome", "trade_category", "is_swing_trade", "trade_symbol"}
            if not required_columns.issubset(set(df.columns)):
                messages.error(request, f"Missing required columns: {required_columns - set(df.columns)}")
                return redirect("import_trades")

            for _, row in df.iterrows():
                # Optional: Add duplicate check here
                JournalTrade.objects.create(
                    trade_type=row["trade_type"],
                    trade_setup_strategy=row["trade_setup_strategy"],
                    trade_direction=row["trade_direction"],
                    quantity=row["quantity"],
                    entry_price=row["entry_price"],
                    exit_price=row["exit_price"],
                    exit_date=row["exit_date"],
                    target_price=row["target_price"],
                    stop_loss_price=row["stop_loss_price"],
                    fees=row["fees"],
                    trade_return=row["trade_return"],
                    risk_reward_ratio=row["risk_reward_ratio"],
                    notes=row["notes"],
                    trade_outcome=row["trade_outcome"],
                    trade_category=row["trade_category"],
                    is_swing_trade=row["is_swing_trade"],
                    trade_symbol=row["trade_symbol"],
                    user=request.user
                )
            messages.success(request, "Trades imported successfully.")
        except Exception as e:
            messages.error(request, f"Error importing trades: {e}")
        return redirect("import_trades")

    return render(request, "import_trades.html")



####Test import

# import pandas as pd
# from django.shortcuts import render, redirect
# from django.contrib import messages
# from .models import JournalTrade
# from .forms import TradeImportForm

# def import_trades(request):
#     if request.method == 'POST':
#         form = TradeImportForm(request.POST, request.FILES)
#         if form.is_valid():
#             file = request.FILES['file']
#             ext = file.name.split('.')[-1].lower()

#             try:
#                 if ext == 'csv':
#                     df = pd.read_csv(file)
#                 elif ext == 'xlsx':
#                     df = pd.read_excel(file, engine='openpyxl')
#                 else:
#                     messages.error(request, "Only .csv or .xlsx files are supported.")
#                     return redirect('import_trades')

#                 # Optional: Show what was read
#                 print(df.head())

#                 # Validate required columns
#                 required_columns = [
#                     'trade_symbol', 'trade_type', 'trade_setup_strategy', 'trade_direction',
#                     'quantity', 'entry_price', 'exit_price', 'exit_date', 'target_price',
#                     'stop_loss_price', 'fees', 'trade_return', 'risk_reward_ratio',
#                     'notes', 'trade_outcome', 'trade_category', 'is_swing_trade'
#                 ]
#                 for col in required_columns:
#                     if col not in df.columns:
#                         messages.error(request, f"Missing required column: {col}")
#                         return redirect('import_trades')

#                 # Create trade objects
#                 for _, row in df.iterrows():
#                     trade = JournalTrade(
#                         trade_symbol=row['trade_symbol'],
#                         trade_type=row['trade_type'],
#                         trade_setup_strategy=row['trade_setup_strategy'],
#                         trade_direction=row['trade_direction'],
#                         quantity=row['quantity'],
#                         entry_price=row['entry_price'],
#                         exit_price=row['exit_price'],
#                         exit_date=row['exit_date'],
#                         target_price=row['target_price'],
#                         stop_loss_price=row['stop_loss_price'],
#                         fees=row['fees'],
#                         trade_return=row['trade_return'],
#                         risk_reward_ratio=row['risk_reward_ratio'],
#                         notes=row['notes'],
#                         trade_outcome=row['trade_outcome'],
#                         trade_category=row['trade_category'],
#                         is_swing_trade=row['is_swing_trade'],
#                         user=request.user
#                     )
#                     trade.save()

#                 messages.success(request, "Trades imported successfully!")
#                 return redirect('trade_list')
#             except Exception as e:
#                 messages.error(request, f"Error importing file: {e}")
#     else:
#         form = TradeImportForm()
    
#     return render(request, 'import_trades.html', {'form': form})




##################### balance test

from .models import AccountTransaction
from .forms import DepositWithdrawForm

####TEST 1

# def get_current_balance(user):
#     transactions = AccountTransaction.objects.filter(user=user)
#     return sum(t.amount if t.transaction_type != 'withdrawal' else -t.amount for t in transactions)


# def add_transaction(request):
#     if request.method == 'POST':
#         form = DepositWithdrawForm(request.POST)
#         if form.is_valid():
#             trans = form.save(commit=False)
#             trans.user = request.user
#             if trans.transaction_type == 'withdrawal':
#                 trans.amount *= -1  # make it negative
#             trans.save()
#             messages.success(request, "Transaction recorded!")
#             return redirect('balance_history')
#     else:
#         form = DepositWithdrawForm()

#     balance = get_current_balance(request.user)
#     return render(request, 'balance_history.html', {'form': form, 'balance': balance})


# def balance_history(request):
#     transactions = AccountTransaction.objects.filter(user=request.user).order_by('-created_at')
#     balance = get_current_balance(request.user)
#     return render(request, 'balance_history.html', {
#         'transactions': transactions,
#         'balance': balance
#     })

### END TEST 1

### start test 2

# from django.shortcuts import render, redirect
# from django.contrib import messages
# from .models import AccountTransaction
# from .forms import DepositWithdrawForm

# # Utility to get current balance
# def get_current_balance(user):
#     transactions = AccountTransaction.objects.filter(user=user)
#     balance = 0
#     for t in transactions:
#         if t.transaction_type == 'withdrawal':
#             balance -= abs(t.amount)
#         else:
#             balance += t.amount
#     return round(balance, 2)

# # Add deposit or withdrawal (POST handler only)
# def add_transaction(request):
#     if request.method == 'POST':
#         form = DepositWithdrawForm(request.POST)
#         if form.is_valid():
#             tx = form.save(commit=False)
#             tx.user = request.user

#             # Normalize: withdrawal is always stored as positive, subtracted in view logic
#             if tx.transaction_type == 'withdrawal' and tx.amount < 0:
#                 tx.amount = abs(tx.amount)

#             tx.save()
#             messages.success(request, f"{tx.transaction_type.capitalize()} added!")
#             return redirect('balance_history')
#         else:
#             messages.error(request, "Invalid form data.")
#             return redirect('balance_history')
#     else:
#         return redirect('balance_history')

# # Full balance & transaction history page
# def balance_history(request):
#     transactions = AccountTransaction.objects.filter(user=request.user).order_by('-created_at')
#     balance = get_current_balance(request.user)
#     form = DepositWithdrawForm()

#     return render(request, 'balance_history.html', {
#         'balance': balance,
#         'transactions': transactions,
#         'form': form,
#     })


### end test 2

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import AccountTransaction
from .forms import DepositWithdrawForm
from django.db.models import Sum, Count
from datetime import datetime
from .models import JournalTrade


@login_required
def get_current_balance(request, transactions=None):
    if transactions is None:
        transactions = AccountTransaction.objects.filter(user=request.user)
    balance = 0
    for t in transactions.order_by('created_at'):
        if t.transaction_type == 'withdrawal':
            balance -= abs(t.amount)
        else:
            balance += t.amount
    return round(balance, 2)


@login_required
def balance_history(request):
    # Trade outcome counts
    # Trade outcomes (all-time or filtered, your choice)
    outcome_data = {
        'win': 0,
        'loss': 0,
        'breakeven': 0,
    }
    outcome_qs = JournalTrade.objects.filter(user=request.user)
    outcomes = outcome_qs.values('trade_outcome').annotate(count=Count('id'))
    for item in outcomes:
        if item['trade_outcome'] in outcome_data:
            outcome_data[item['trade_outcome']] = item['count']
    # Filters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    qs = AccountTransaction.objects.filter(user=request.user)
    if start_date:
        try:
            qs = qs.filter(created_at__date__gte=datetime.fromisoformat(start_date).date())
        except Exception:
            pass
    if end_date:
        try:
            qs = qs.filter(created_at__date__lte=datetime.fromisoformat(end_date).date())
        except Exception:
            pass

    qs = qs.order_by('created_at')  # ascending for running balance

    # Compute running balances
    running = []
    bal = 0
    for t in qs:
        if t.transaction_type == 'withdrawal':
            bal -= abs(t.amount)
        else:
            bal += t.amount
        running.append({
            'transaction': t,
            'running_balance': round(bal, 2)
        })

    # Summary for chart: total deposits vs withdrawals in this filtered window
    deposits_sum = qs.filter(transaction_type='deposit').aggregate(total=Sum('amount'))['total'] or 0
    withdrawals_sum = qs.filter(transaction_type='withdrawal').aggregate(total=Sum('amount'))['total'] or 0
    balance =  get_current_balance(request)
    print("balance: ", balance)
    print("USERRRRRRRRRR ::",AccountTransaction.objects.filter(user=request.user))
    # current_balance = get_current_balance(request.user, transactions=AccountTransaction.objects.filter(user=request.user, created_at__lte=qs.last().created_at) if qs.exists() else None)

    form = DepositWithdrawForm()

    context = {
        'running': running,  # list of dicts with transaction and running_balance
        'balance': get_current_balance(request),  # overall current balance
        'form': form,
        'start_date': start_date,
        'end_date': end_date,
        'deposits_sum': float(deposits_sum),
        'withdrawals_sum': float(withdrawals_sum),
        'combined_chart_data': {
            'deposits': float(deposits_sum),
            'withdrawals': float(withdrawals_sum),
            'wins': outcome_data['win'],
            'losses': outcome_data['loss'],
            'breakeven': outcome_data['breakeven'],
        }
    }
    return render(request, 'balance_history.html', context)


@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = DepositWithdrawForm(request.POST)
        if form.is_valid():
            tx = form.save(commit=False)
            tx.user = request.user
            tx.save()
            messages.success(request, f"{tx.transaction_type.capitalize()} added!")
            return redirect('balance_history')
        else:
            messages.error(request, "Invalid form data.")
    return redirect('balance_history')



##################################analytics

from django.shortcuts import render

def analytics_dashboard(request):
    context = {
        'open_trades': 149,
        'total_exposure': 164063026.67,
        'win_rate': 46.4,
        'total_profit_loss': 23888882.91,
        'account_balance': 200546.38,
        'deposited_capital': 104007026.77,
        'realized_pnl': 13288248.91,
        'return_percent': 238.5,
        'best_trade': 650278.00,
        'worst_trade': -2017790.00,
        'consecutive_wins': 10,
        'consecutive_losses': 2,
        'avg_time_in_trade': 6,
        'rr_ratio': 2.81,

        'win_count': 70,
        'loss_count': 80,
        'long_count': 100,
        'short_count': 50,

        'mood_labels': ['Calm', 'Anxious', 'Overconfident'],
        'mood_data': [60, 25, 15],

        'equity_curve_dates': ['Jul 1', 'Jul 5', 'Jul 10', 'Jul 15'],
        'equity_curve_values': [100000, 115000, 110000, 130000],

        'monthly_labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
        'monthly_values': [1000, -500, 3000, -1000, 8000],
    }
    return render(request, 'analytics_dashboard.html', context)
