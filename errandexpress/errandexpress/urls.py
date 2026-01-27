from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views
from django.views.generic import RedirectView, TemplateView

urlpatterns = [
    path('admin/', RedirectView.as_view(pattern_name='admin_dashboard', permanent=False)),
    path('admin/database/', admin.site.urls),
    path('health/', views.health_check, name='health_check'),
    path('', views.home, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('pending-ratings/', views.pending_ratings, name='pending_ratings'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('guide/', TemplateView.as_view(template_name='guide.html'), name='guide'),
    
    # Legal Pages
    path('terms/', views.terms_of_service, name='terms_of_service'),
    path('privacy/', views.privacy_policy, name='privacy_policy'),
    
    # Task Management
    path('tasks/create/', views.create_task, name='create_task'),
    path('tasks/<uuid:task_id>/edit/', views.edit_task, name='edit_task'),
    path('tasks/browse/', views.browse_tasks, name='browse_tasks'),
    path('tasks/<uuid:task_id>/', views.task_detail, name='task_detail'),
    path('tasks/<uuid:task_id>/accept/', views.accept_task, name='accept_task'),
    path('tasks/<uuid:task_id>/complete/', views.complete_task, name='complete_task'),
    path('tasks/<uuid:task_id>/message/', views.send_message, name='send_message'),
    path('my-tasks/', views.my_tasks, name='my_tasks'),
    
    # Task Application System
    path('tasks/<uuid:task_id>/apply/', views.apply_for_task, name='apply_for_task'),
    path('tasks/<uuid:task_id>/applications/', views.view_applications, name='view_applications'),
    path('application/<uuid:application_id>/accept/', views.accept_application, name='accept_application'),
    path('application/<uuid:application_id>/reject/', views.reject_application, name='reject_application'),
    
    # Skill Validation
    path('skills/', views.skill_validation, name='skill_validation'),
    path('skills/typing-test/<uuid:skill_id>/', views.typing_test, name='typing_test'),
    path('skills/delete/<uuid:skill_id>/', views.delete_skill, name='delete_skill'),
    
    # Payment System
    path('payment/system-fee/<uuid:task_id>/', views.payment_system_fee, name='payment_system_fee'),
    path('payment/commission/<uuid:task_id>/', views.payment_commission, name='payment_commission'),
    path('payment/commission-process/<uuid:task_id>/', views.payment_commission_process, name='payment_commission_process'),
    path('payment/task-doer/<uuid:task_id>/', views.payment_task_doer, name='payment_task_doer'),
    path('payment/task-doer-process/<uuid:task_id>/', views.payment_task_doer_process, name='payment_task_doer_process'),
    path('payment/task-doer-card/<uuid:task_id>/', views.payment_task_doer_card, name='payment_task_doer_card'),
    path('payment/gcash-form/<uuid:task_id>/', views.gcash_payment_form, name='gcash_payment_form'),
    path('payment/gcash-process/<uuid:task_id>/', views.gcash_payment_process, name='gcash_payment_process'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/failed/', views.payment_failed, name='payment_failed'),
    path('test/confirm-payment/<uuid:task_id>/', views.test_confirm_payment, name='test_confirm_payment'),  # TEST ONLY
    path('test/manual-payment-confirm/<uuid:task_id>/', views.test_manual_payment_confirm, name='test_manual_payment_confirm'),  # TEST ONLY
    
    # Payment APIs
    path('api/create-payment-intent/', views.create_payment_intent, name='create_payment_intent'),
    path('api/create-gcash-payment/', views.create_gcash_payment, name='create_gcash_payment'),
    path('api/create-card-payment/', views.create_card_payment, name='create_card_payment'),
    path('api/create-task-payment-intent/', views.create_task_payment_intent, name='create_task_payment_intent'),
    path('api/create-task-gcash-payment/', views.create_task_gcash_payment, name='create_task_gcash_payment'),
    path('api/create-task-card-payment/', views.create_task_card_payment, name='create_task_card_payment'),
    
    # Card Payment Form
    path('payments/card-form/<uuid:task_id>/', views.card_payment_form, name='card_payment_form'),
    
    # Rating and Reporting
    path('rate/<uuid:task_id>/<uuid:user_id>/', views.rate_user, name='rate_user'),
    path('report/<uuid:user_id>/', views.report_user, name='report_user'),
    
    # Messages/Chat
    path('messages/', views.messages_list, name='messages_list'),
    path('messages/<uuid:task_id>/', views.messages_list, name='messages_chat'),
    path('chat/<uuid:task_id>/', views.chat_view, name='chat_view'),
    
    # Payments
    path('payments/', views.payments_dashboard, name='payments_dashboard'),
    
    # Settings
    path('settings/', views.settings_view, name='settings'),
    
    # Notifications
    path('notifications/', views.notifications, name='notifications'),
    path('api/notification-count/', views.notification_count, name='notification_count'),
    path('api/notifications/recent/', views.api_notifications_recent, name='api_notifications_recent'),
    path('api/notifications/count/', views.api_notifications_count, name='api_notifications_count'),
    path('api/notifications/mark-as-read/', views.api_notifications_mark_as_read, name='api_notifications_mark_as_read'),
    path('api/tasks/updates/', views.api_tasks_updates, name='api_tasks_updates'),
    
    # Monitoring
    path('monitoring/', views.task_monitoring, name='task_monitoring'),
    
    # Feedback APIs
    path('api/submit-feedback/<uuid:task_id>/', views.api_submit_feedback, name='api_submit_feedback'),
    path('api/get-feedback/<uuid:task_id>/', views.api_get_task_feedback, name='api_get_task_feedback'),
    
    # Payment APIs
    path('api/payment-details/<uuid:payment_id>/', views.api_payment_details, name='api_payment_details'),
    path('api/download-receipt/<uuid:payment_id>/', views.api_download_receipt, name='api_download_receipt'),
    
    # Smart Algorithm APIs
    path('api/auto-assign/<uuid:task_id>/', views.api_auto_assign_task, name='api_auto_assign_task'),
    path('api/manual-assign/<uuid:task_id>/', views.api_manual_assign_task, name='api_manual_assign_task'),
    path('api/reassign/<uuid:assignment_id>/', views.api_reassign_task, name='api_reassign_task'),
    path('api/check-chat/<uuid:task_id>/', views.api_check_chat_access, name='api_check_chat_access'),
    path('api/unlock-chat/<uuid:task_id>/', views.api_unlock_chat_after_payment, name='api_unlock_chat'),
    path('api/send-message/', views.api_send_message, name='api_send_message'),
    path('api/messages/<uuid:task_id>/', views.api_get_messages, name='api_get_messages'),
    
    # PayMongo Live Integration
    path('api/create-payment-intent/', views.create_payment_intent, name='create_payment_intent'),
    path('api/create-gcash-payment/', views.create_gcash_payment, name='create_gcash_payment'),
    path('webhook/paymongo/', views.paymongo_webhook, name='paymongo_webhook'),
    path('test-paymongo/', views.test_paymongo_integration, name='test_paymongo'),
    
    # Task Completion Payment APIs
    path('api/complete-task-payment/<uuid:task_id>/', views.api_complete_task_payment, name='api_complete_task_payment'),
    path('api/confirm-cod-payment/<uuid:payment_id>/', views.api_confirm_cod_payment, name='api_confirm_cod_payment'),
    path('api/confirm-cod-receipt/<uuid:payment_id>/', views.api_confirm_cod_receipt, name='api_confirm_cod_receipt'),
    path('api/check-payment-status/', views.api_check_payment_status, name='api_check_payment_status'),
    path('api/create-task-payment-intent/', views.create_task_payment_intent, name='create_task_payment_intent'),
    path('api/create-task-gcash-payment/', views.create_task_gcash_payment, name='create_task_gcash_payment'),
    
    # Admin Dashboard
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/users/', views.admin_users, name='admin_users'),
    path('admin-dashboard/tasks/', views.admin_tasks, name='admin_tasks'),
    path('admin-dashboard/skills/', views.admin_skill_validation, name='admin_skill_validation'),
    path('system-wallet/', views.system_wallet, name='system_wallet'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
