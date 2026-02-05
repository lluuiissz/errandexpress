"""Script to append new models to models.py"""

new_models_code = '''

class DoerAvailability(models.Model):
    """Track doer availability schedules (OBJECTIVE NO.1 Enhancement)"""
    DAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    doer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='availability_slots')
    day_of_week = models.IntegerField(choices=DAY_CHOICES, help_text="Day of the week (0=Monday, 6=Sunday)")
    start_time = models.TimeField(help_text="Availability start time")
    end_time = models.TimeField(help_text="Availability end time")
    is_available = models.BooleanField(default=True, help_text="Currently available")
    recurring = models.BooleanField(default=True, help_text="Repeats weekly")
    notes = models.TextField(blank=True, help_text="Additional notes about availability")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Doer Availability"
        verbose_name_plural = "Doer Availabilities"
        ordering = ['day_of_week', 'start_time']
        unique_together = ['doer', 'day_of_week', 'start_time']
        indexes = [
            models.Index(fields=['doer', 'day_of_week']),
            models.Index(fields=['doer', 'is_available']),
        ]
    
    def __str__(self):
        return f"{self.doer.fullname} - {self.get_day_of_week_display()} {self.start_time.strftime('%H:%M')}-{self.end_time.strftime('%H:%M')}"
    
    def is_available_at(self, check_datetime):
        """Check if doer is available at specific datetime"""
        if not self.is_available:
            return False
        
        # Check day of week matches
        if check_datetime.weekday() != self.day_of_week:
            return False
        
        # Check time is within range
        check_time = check_datetime.time()
        return self.start_time <= check_time <= self.end_time


class TaskSchedule(models.Model):
    """Advanced task scheduling (OBJECTIVE NO.1 Enhancement)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.OneToOneField(Task, on_delete=models.CASCADE, related_name='schedule')
    scheduled_start = models.DateTimeField(help_text="Scheduled start time")
    scheduled_end = models.DateTimeField(help_text="Scheduled end time")
    buffer_time = models.DurationField(
        default=timezone.timedelta(minutes=30),
        help_text="Buffer time before/after task"
    )
    auto_reschedule = models.BooleanField(
        default=False,
        help_text="Automatically reschedule if conflicts arise"
    )
    priority_level = models.IntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Scheduling priority (1=Low, 5=Urgent)"
    )
    is_confirmed = models.BooleanField(default=False, help_text="Schedule confirmed by doer")
    confirmed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, help_text="Scheduling notes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Task Schedule"
        verbose_name_plural = "Task Schedules"
        ordering = ['scheduled_start']
        indexes = [
            models.Index(fields=['scheduled_start']),
            models.Index(fields=['task', 'is_confirmed']),
            models.Index(fields=['priority_level', '-scheduled_start']),
        ]
    
    def __str__(self):
        return f"{self.task.title} - {self.scheduled_start.strftime('%Y-%m-%d %H:%M')}"
    
    def has_conflict_with(self, other_schedule):
        """Check if this schedule conflicts with another"""
        # Add buffer time to both schedules
        self_start = self.scheduled_start - self.buffer_time
        self_end = self.scheduled_end + self.buffer_time
        other_start = other_schedule.scheduled_start - other_schedule.buffer_time
        other_end = other_schedule.scheduled_end + other_schedule.buffer_time
        
        # Check for overlap
        return not (self_end <= other_start or self_start >= other_end)
    
    def confirm_schedule(self):
        """Confirm the schedule"""
        self.is_confirmed = True
        self.confirmed_at = timezone.now()
        self.save()
'''

# Append to models.py
models_path = r'c:\Users\Admin\Desktop\errandexpress - bottle neck\errandexpress\core\models.py'

with open(models_path, 'a', encoding='utf-8') as f:
    f.write(new_models_code)

print("✅ Successfully appended DoerAvailability and TaskSchedule models to models.py")
