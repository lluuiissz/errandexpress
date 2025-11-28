# Generated migration for adding database indexes

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_adminlog'),
    ]

    operations = [
        # Add indexes to Task model
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['status'], name='task_status_idx'),
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['poster'], name='task_poster_idx'),
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['doer'], name='task_doer_idx'),
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['created_at'], name='task_created_idx'),
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['status', 'created_at'], name='task_status_created_idx'),
        ),
        
        # Add indexes to Message model
        migrations.AddIndex(
            model_name='message',
            index=models.Index(fields=['task'], name='message_task_idx'),
        ),
        migrations.AddIndex(
            model_name='message',
            index=models.Index(fields=['sender'], name='message_sender_idx'),
        ),
        migrations.AddIndex(
            model_name='message',
            index=models.Index(fields=['created_at'], name='message_created_idx'),
        ),
        migrations.AddIndex(
            model_name='message',
            index=models.Index(fields=['task', 'created_at'], name='message_task_created_idx'),
        ),
    ]
