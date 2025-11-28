from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone
from .models import (
    User, StudentSkill, Task, TaskApplication, Message, SystemCommission, 
    Rating, Report, Payment, Notification, AdminLog, SystemWallet
)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'fullname', 'email', 'role', 'avg_rating', 'is_verified', 'is_banned')
    list_filter = ('role', 'doer_type', 'is_verified', 'is_banned', 'date_joined')
    search_fields = ('username', 'fullname', 'email')
    ordering = ('-date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('ErrandExpress Profile', {
            'fields': ('fullname', 'role', 'doer_type', 'avg_rating', 'total_ratings', 
                      'is_verified', 'phone_number', 'profile_picture', 'bio', 
                      'is_banned', 'ban_reason')
        }),
    )


@admin.register(StudentSkill)
class StudentSkillAdmin(admin.ModelAdmin):
    list_display = ('student', 'skill_name', 'status', 'test_score', 'created_at')
    list_filter = ('skill_name', 'status', 'created_at')
    search_fields = ('student__fullname', 'student__username')
    actions = ['approve_skills', 'reject_skills']
    
    def approve_skills(self, request, queryset):
        queryset.update(status='verified', verified_by=request.user, verified_at=timezone.now())
    approve_skills.short_description = "Approve selected skills"
    
    def reject_skills(self, request, queryset):
        queryset.update(status='rejected', verified_by=request.user, verified_at=timezone.now())
    reject_skills.short_description = "Reject selected skills"


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'poster', 'doer', 'category', 'price', 'status', 'created_at')
    list_filter = ('category', 'status', 'payment_method', 'created_at')
    search_fields = ('title', 'poster__fullname', 'doer__fullname')
    readonly_fields = ('created_at', 'updated_at', 'accepted_at', 'completed_at')


@admin.register(TaskApplication)
class TaskApplicationAdmin(admin.ModelAdmin):
    list_display = ('task', 'doer', 'status', 'doer_rating_snapshot', 'doer_is_newbie', 'ranking_score', 'created_at')
    list_filter = ('status', 'doer_is_newbie', 'created_at')
    search_fields = ('task__title', 'doer__fullname', 'cover_letter')
    readonly_fields = ('doer_rating_snapshot', 'doer_completed_tasks_snapshot', 'doer_is_newbie', 'created_at', 'reviewed_at')
    actions = ['accept_applications', 'reject_applications']
    
    def ranking_score(self, obj):
        return f"{obj.ranking_score:.1f}"
    ranking_score.short_description = "Ranking Score"
    
    def accept_applications(self, request, queryset):
        for app in queryset:
            app.status = 'accepted'
            app.reviewed_at = timezone.now()
            app.save()
            # Assign doer to task
            app.task.doer = app.doer
            app.task.status = 'accepted'
            app.task.accepted_at = timezone.now()
            app.task.save()
    accept_applications.short_description = "Accept selected applications"
    
    def reject_applications(self, request, queryset):
        queryset.update(status='rejected', reviewed_at=timezone.now())
    reject_applications.short_description = "Reject selected applications"


@admin.register(SystemCommission)
class SystemCommissionAdmin(admin.ModelAdmin):
    list_display = ('task', 'payer', 'amount', 'method', 'status', 'created_at')
    list_filter = ('method', 'status', 'created_at')
    search_fields = ('task__title', 'payer__fullname')
    readonly_fields = ('created_at', 'paid_at')


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('task', 'rater', 'rated', 'score', 'created_at')
    list_filter = ('score', 'created_at')
    search_fields = ('task__title', 'rater__fullname', 'rated__fullname')


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('reporter', 'reported', 'reason', 'status', 'created_at')
    list_filter = ('reason', 'status', 'created_at')
    search_fields = ('reporter__fullname', 'reported__fullname')
    actions = ['mark_resolved', 'mark_dismissed']
    
    def mark_resolved(self, request, queryset):
        queryset.update(status='resolved', handled_by=request.user, resolved_at=timezone.now())
    mark_resolved.short_description = "Mark as resolved"
    
    def mark_dismissed(self, request, queryset):
        queryset.update(status='dismissed', handled_by=request.user, resolved_at=timezone.now())
    mark_dismissed.short_description = "Mark as dismissed"


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('task', 'payer', 'receiver', 'amount', 'method', 'status', 'created_at')
    list_filter = ('method', 'status', 'created_at')
    search_fields = ('task__title', 'payer__fullname', 'receiver__fullname')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('task', 'sender', 'message_preview', 'is_proof', 'created_at')
    list_filter = ('is_proof', 'created_at')
    search_fields = ('task__title', 'sender__fullname', 'message')
    
    def message_preview(self, obj):
        return obj.message[:50] + "..." if len(obj.message) > 50 else obj.message
    message_preview.short_description = "Message"


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'title', 'is_read', 'created_at')
    list_filter = ('type', 'is_read', 'created_at')
    search_fields = ('user__fullname', 'title', 'message')


@admin.register(AdminLog)
class AdminLogAdmin(admin.ModelAdmin):
    list_display = ('admin', 'action', 'target_user', 'description_preview', 'ip_address', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('admin__fullname', 'target_user__fullname', 'description')
    readonly_fields = ('admin', 'action', 'target_user', 'target_task', 'target_skill', 
                      'target_report', 'description', 'ip_address', 'user_agent', 'created_at')
    
    def description_preview(self, obj):
        return obj.description[:75] + "..." if len(obj.description) > 75 else obj.description
    description_preview.short_description = "Description"
    
    def has_add_permission(self, request):
        # Prevent manual creation of logs through admin
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of audit logs
        return False


@admin.register(SystemWallet)
class SystemWalletAdmin(admin.ModelAdmin):
    list_display = ('total_revenue', 'total_transactions', 'created_at', 'updated_at')
    readonly_fields = ('total_revenue', 'total_transactions', 'created_at', 'updated_at')
    
    def has_add_permission(self, request):
        # Only one wallet should exist
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of wallet
        return False
