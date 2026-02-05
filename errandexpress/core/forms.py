from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Task, TaskApplication, StudentSkill, Rating, Report, Message
import datetime


class TaskForm(forms.ModelForm):
    """Form for creating and editing tasks"""
    
    class Meta:
        model = Task
        fields = ['title', 'description', 'category', 'tags', 'price', 'payment_method', 
                 'deadline', 'location', 'campus_location', 'requirements',
                 'time_window_start', 'time_window_end', 'preferred_delivery_time',
                 'flexible_timing', 'preferred_doer', 'priority_level']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter a clear, descriptive title',
                'style': 'height: 40px; width: 100%; font-size: 14px;'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Provide detailed description of what needs to be done'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
                'style': 'height: 40px; width: 100%; font-size: 14px;'
            }),
            'tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., urgent, easy, typing, graphics (comma-separated)',
                'style': 'height: 40px; width: 100%; font-size: 14px;'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '10',
                'step': '0.01',
                'placeholder': '0.00',
                'style': 'height: 40px; width: 100%; font-size: 14px;'
            }),
            'payment_method': forms.Select(attrs={
                'class': 'form-select',
                'style': 'height: 40px; width: 100%; font-size: 14px;'
            }),
            'deadline': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'style': 'height: 40px; width: 100%; font-size: 14px;'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Specific location (e.g. Room 305)',
                'style': 'height: 40px; width: 100%; font-size: 14px;'
            }),
            'campus_location': forms.Select(attrs={
                'class': 'form-select',
                'style': 'height: 40px; width: 100%; font-size: 14px;'
            }),
            'requirements': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Special requirements or qualifications needed'
            }),
            'time_window_start': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'style': 'height: 40px; width: 100%; font-size: 14px;'
            }),
            'time_window_end': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'style': 'height: 40px; width: 100%; font-size: 14px;'
            }),
            'preferred_delivery_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
                'style': 'height: 40px; width: 100%; font-size: 14px;'
            }),
            'flexible_timing': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'style': 'width: 20px; height: 20px;'
            }),
            'preferred_doer': forms.Select(attrs={
                'class': 'form-select',
                'style': 'height: 40px; width: 100%; font-size: 14px;'
            }),
            'priority_level': forms.Select(attrs={
                'class': 'form-select',
                'style': 'height: 40px; width: 100%; font-size: 14px;'
            })
        }
    
    PRIORITY_CHOICES = [
        (1, '⭐ Low Priority'),
        (2, '⭐⭐ Below Normal'),
        (3, '⭐⭐⭐ Normal'),
        (4, '⭐⭐⭐⭐ High Priority'),
        (5, '⭐⭐⭐⭐⭐ Urgent')
    ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate preferred_doer choices with task doers
        from .models import User
        self.fields['preferred_doer'].queryset = User.objects.filter(
            role='task_doer', is_active=True
        ).order_by('fullname')
        self.fields['preferred_doer'].required = False
        self.fields['preferred_doer'].empty_label = "No preference"
        
        # Set priority level choices and widget
        self.fields['priority_level'].widget.choices = self.PRIORITY_CHOICES
        self.fields['priority_level'].choices = self.PRIORITY_CHOICES
        self.fields['priority_level'].initial = 3
        self.fields['priority_level'].required = False
        
        # Make new fields optional
        self.fields['time_window_start'].required = False
        self.fields['time_window_end'].required = False
        self.fields['preferred_delivery_time'].required = False
        self.fields['flexible_timing'].required = False
    
    
    def clean_deadline(self):
        deadline = self.cleaned_data.get('deadline')
        if deadline and deadline <= timezone.now():
            raise ValidationError("Deadline must be in the future.")
        return deadline
    
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price and price < 10:
            raise ValidationError("Minimum task price is ₱10.")
        return price


class TaskApplicationForm(forms.ModelForm):
    """Form for applying to tasks"""
    
    class Meta:
        model = TaskApplication
        fields = ['cover_letter', 'proposed_timeline']
        widgets = {
            'cover_letter': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Explain why you are the best fit for this task. Mention your relevant experience and skills...',
                'required': True,
                'maxlength': '50'
            }),
            'proposed_timeline': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., "I can complete this within 2 days" (optional)'
            })
        }
    
    def clean_cover_letter(self):
        cover_letter = self.cleaned_data.get('cover_letter')
        if cover_letter and len(cover_letter) > 50:
            raise ValidationError("Please keep your explanation short (maximum 50 characters).")
        return cover_letter


class TaskFilterForm(forms.Form):
    """Form for filtering and searching tasks"""
    
    SORT_CHOICES = [
        ('smart', '✨ Recommended'),
        ('-created_at', 'Newest First'),
        ('created_at', 'Oldest First'),
        ('price', 'Price: Low to High'),
        ('-price', 'Price: High to Low'),
        ('deadline', 'Deadline: Soonest First'),
    ]
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search tasks...'
        })
    )
    
    category = forms.ChoiceField(
        choices=[('', 'All Categories')] + Task.CATEGORY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    min_price = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min ₱'
        })
    )
    
    max_price = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max ₱'
        })
    )
    
    sort_by = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        initial='smart',
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class SkillValidationForm(forms.ModelForm):
    """Form for skill validation requests"""
    
    class Meta:
        model = StudentSkill
        fields = ['skill_name', 'proof_url', 'notes']
        widgets = {
            'skill_name': forms.Select(attrs={'class': 'form-select'}),
            'proof_url': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional information about your skill or experience'
            })
        }


class MessageForm(forms.ModelForm):
    """Form for sending messages"""
    
    class Meta:
        model = Message
        fields = ['message', 'attachment']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Type your message...'
            }),
            'attachment': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png,.zip'
            })
        }


class RatingForm(forms.ModelForm):
    """Form for rating users"""
    
    class Meta:
        model = Rating
        fields = ['score', 'feedback']
        widgets = {
            'score': forms.Select(
                choices=[(i, f"{i}/10") for i in range(1, 11)],
                attrs={'class': 'form-select'}
            ),
            'feedback': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share your experience working with this user...'
            })
        }


class ReportForm(forms.ModelForm):
    """Form for reporting users"""
    
    class Meta:
        model = Report
        fields = ['reason', 'description']
        widgets = {
            'reason': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Please provide details about the issue...'
            })
        }


class ProfileUpdateForm(forms.ModelForm):
    """Form for updating user profile"""
    
    class Meta:
        model = Task._meta.get_field('poster').related_model  # User model
        fields = ['fullname', 'phone_number', 'bio', 'profile_picture']
        widgets = {
            'fullname': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+63 XXX XXX XXXX'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell others about yourself...'
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.jpg,.jpeg,.png'
            })
        }
