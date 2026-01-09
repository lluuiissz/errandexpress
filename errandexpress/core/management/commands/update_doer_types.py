"""
Management command to update doer_type for users with verified skills

This fixes existing users who have verified skills but incorrect doer_type.
Run once after deploying the automatic update feature.
"""
from django.core.management.base import BaseCommand
from core.models import User, StudentSkill


class Command(BaseCommand):
    help = 'Update doer_type for users with verified skills'

    def handle(self, *args, **options):
        self.stdout.write('🔍 Checking users with verified skills...\n')
        
        # Find users with verified skills but doer_type is 'microtasker' or None
        users_to_update = User.objects.filter(
            role='task_doer',
            skills__status='verified',
            doer_type__in=['microtasker', None]
        ).distinct()
        
        count = users_to_update.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('✅ No users need updating'))
            return
        
        self.stdout.write(f'Found {count} user(s) to update:\n')
        
        updated_count = 0
        for user in users_to_update:
            # Get their verified skills
            verified_skills = list(
                user.skills.filter(status='verified').values_list('skill_name', flat=True)
            )
            
            self.stdout.write(
                f'  - {user.username} ({user.fullname})\n'
                f'    Current doer_type: {user.doer_type}\n'
                f'    Verified skills: {", ".join(verified_skills)}'
            )
            
            # Update to 'both'
            user.doer_type = 'both'
            user.save(update_fields=['doer_type'])
            updated_count += 1
            
            self.stdout.write(
                self.style.SUCCESS(f'    ✅ Updated to doer_type="both"\n')
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Successfully updated {updated_count} user(s)'
            )
        )
