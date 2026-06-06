# Generated migration for performance indexes
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_task_campus_location_user_campus_location'),
    ]

    operations = [
        # ========================================
        # NOTIFICATION INDEXES
        # ========================================
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['user', 'is_read'], name='notif_user_read_idx'),
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['user', '-created_at'], name='notif_user_created_idx'),
        ),
        
        # ========================================
        # MESSAGE INDEXES
        # ========================================
        migrations.AddIndex(
            model_name='message',
            index=models.Index(fields=['is_read'], name='msg_read_idx'),
        ),
        migrations.AddIndex(
            model_name='message',
            index=models.Index(fields=['task', '-created_at'], name='msg_task_created_idx'),
        ),
        
        # ========================================
        # TASK INDEXES
        # ========================================
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['status', '-created_at'], name='task_status_created_idx'),
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['poster', 'status'], name='task_poster_status_idx'),
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['doer', 'status'], name='task_doer_status_idx'),
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['category', 'status'], name='task_category_status_idx'),
        ),
        
        # ========================================
        # TASK APPLICATION INDEXES
        # ========================================
        migrations.AddIndex(
            model_name='taskapplication',
            index=models.Index(fields=['task', 'status'], name='app_task_status_idx'),
        ),
        migrations.AddIndex(
            model_name='taskapplication',
            index=models.Index(fields=['doer', 'status'], name='app_doer_status_idx'),
        ),
        
        # ========================================
        # PAYMENT INDEXES
        # ========================================
        migrations.AddIndex(
            model_name='payment',
            index=models.Index(fields=['status'], name='payment_status_idx'),
        ),
        migrations.AddIndex(
            model_name='payment',
            index=models.Index(fields=['task', 'status'], name='payment_task_status_idx'),
        ),
    ]
