"""
Management command to fix naive datetimes in the database
Run with: py manage.py fix_timezones
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import (
    Payment, SystemCommission, TaskApplication, 
    Rating, Task, Message, Notification, Report
)


class Command(BaseCommand):
    help = 'Fix naive datetimes in database by converting them to timezone-aware'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be fixed without actually fixing',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        fixed_count = 0
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        # Models to check
        models_to_check = [
            (Payment, ['created_at', 'confirmed_at']),
            (SystemCommission, ['created_at', 'paid_at']),
            (TaskApplication, ['created_at', 'reviewed_at']),
            (Rating, ['created_at']),
            (Task, ['created_at', 'accepted_at', 'completed_at']),
            (Message, ['created_at']),
            (Notification, ['created_at']),
            (Report, ['created_at', 'resolved_at']),
        ]
        
        for model, fields in models_to_check:
            model_name = model.__name__
            self.stdout.write(f'\nChecking {model_name}...')
            
            objects = model.objects.all()
            model_fixed = 0
            
            for obj in objects:
                obj_updated = False
                update_fields = []
                
                for field in fields:
                    try:
                        value = getattr(obj, field, None)
                        
                        if value and timezone.is_naive(value):
                            if not dry_run:
                                # Convert to timezone-aware
                                aware_value = timezone.make_aware(value)
                                setattr(obj, field, aware_value)
                                update_fields.append(field)
                                obj_updated = True
                            
                            self.stdout.write(
                                self.style.WARNING(
                                    f'  - {model_name} {obj.id}: {field} was naive'
                                )
                            )
                            model_fixed += 1
                    except AttributeError:
                        # Field doesn't exist on this model
                        pass
                
                # Save if any fields were updated
                if obj_updated and not dry_run:
                    obj.save(update_fields=update_fields)
            
            if model_fixed > 0:
                fixed_count += model_fixed
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  ✓ Fixed {model_fixed} naive datetime(s) in {model_name}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  ✓ No naive datetimes found in {model_name}'
                    )
                )
        
        # Summary
        self.stdout.write('\n' + '='*50)
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'DRY RUN: Would fix {fixed_count} naive datetime(s)'
                )
            )
            self.stdout.write('Run without --dry-run to apply fixes')
        else:
            if fixed_count > 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Successfully fixed {fixed_count} naive datetime(s)'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        '✓ All datetimes are already timezone-aware!'
                    )
                )
