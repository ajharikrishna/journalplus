from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('trades/', views.trade_list, name='trade_list'),
    path('trade/add/', views.add_trade, name='add_trade'),
    path('trade/<int:pk>/', views.trade_detail, name='trade_detail'),
    path('trade/<int:pk>/edit/', views.edit_trade, name='edit_trade'),
    path('trade/<int:pk>/delete/', views.delete_trade, name='delete_trade'),
    path("import/", views.import_trades, name="import_trades"),

    path('deposits/', views.add_deposit_withdrawal, name='deposits'),
    path('deposit_list/', views.deposit_list, name='deposit_list'),

    path('summary/', views.summary_view, name='summary'),
    path('profile/', views.profile_view, name='profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('reports/', views.export_reports, name='export_reports'),
     path('export/excel/', views.export_excel, name='export_excel'),
    path('export/pdf/', views.export_pdf, name='export_pdf'),
    path('trade-calendar/', views.trade_calendar, name='trade_calendar'),
    path('trade-calendar/<int:year>/<int:month>/', views.trade_calendar, name='trade_calendar_month'),
    
    path('balance/', views.balance_history, name='balance_history'),
    path('balance/add/', views.add_transaction, name='add_transaction'),
     path('analytics/', views.analytics_dashboard, name='analytics'),







]
