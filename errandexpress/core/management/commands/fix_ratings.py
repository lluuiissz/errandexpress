from django.core.management.base import BaseCommand
from core.models import User, Rating
from django.db.models import Avg, Count

class Command(BaseCommand):
    help = 'Recalculates and fixes average ratings for all users'

    def handle(self, *args, **kwargs):
        self.stdout.write('Fixing user ratings...')
        
        users = User.objects.all()
        count = 0
        
        for user in users:
            # Calculate stats from Rating model where this user was RATED
            stats = Rating.objects.filter(rated=user).aggregate(
                avg=Avg('score'),
                total=Count('id')
            )
            
            real_avg = stats['avg'] or 0.0
            real_total = stats['total'] or 0
            
            # Update user
            user.avg_rating = real_avg
            user.total_ratings = real_total
            user.save()
            
            self.stdout.write(f'Updated {user.fullname}: {real_avg} ({real_total} ratings)')
            count += 1
            
        self.stdout.write(self.style.SUCCESS(f'Successfully updated {count} users'))
