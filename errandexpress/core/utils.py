"""
Utility functions for ErrandExpress
"""
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys


def log_admin_action(admin, action, description, request=None, target_user=None, target_task=None, target_skill=None, target_report=None):
    """
    Log admin actions for audit trail
    
    Args:
        admin: User object (admin performing the action)
        action: Action type (from AdminLog.ACTION_CHOICES)
        description: Detailed description of the action
        request: HttpRequest object (optional, for IP and user agent)
        target_user: User object being acted upon (optional)
        target_task: Task object being acted upon (optional)
        target_skill: StudentSkill object being acted upon (optional)
        target_report: Report object being acted upon (optional)
    
    Returns:
        AdminLog object
    """
    from .models import AdminLog
    
    log_data = {
        'admin': admin,
        'action': action,
        'description': description,
        'target_user': target_user,
        'target_task': target_task,
        'target_skill': target_skill,
        'target_report': target_report,
    }
    
    # Extract IP and user agent from request if provided
    if request:
        # Get IP address
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')
        
        log_data['ip_address'] = ip_address
        log_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')[:255]
    
    return AdminLog.objects.create(**log_data)


def compress_image(uploaded_file, max_size=(1920, 1080), quality=85):
    """
    Compress and resize uploaded images automatically
    
    Args:
        uploaded_file: Django UploadedFile object
        max_size: Tuple of (max_width, max_height)
        quality: JPEG quality (1-100)
    
    Returns:
        Compressed InMemoryUploadedFile
    """
    try:
        # Open the image
        img = Image.open(uploaded_file)
        
        # Convert RGBA to RGB if necessary (for PNG with transparency)
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # Resize if image is larger than max_size
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Save to BytesIO
        output = BytesIO()
        
        # Determine format
        format_type = 'JPEG'
        if uploaded_file.name.lower().endswith('.png'):
            format_type = 'PNG'
            quality = 95  # PNG uses different quality scale
        
        img.save(output, format=format_type, quality=quality, optimize=True)
        output.seek(0)
        
        # Create new InMemoryUploadedFile
        compressed_file = InMemoryUploadedFile(
            output,
            'ImageField',
            uploaded_file.name,
            f'image/{format_type.lower()}',
            sys.getsizeof(output),
            None
        )
        
        return compressed_file
    
    except Exception as e:
        # If compression fails, return original file
        print(f"Image compression failed: {e}")
        return uploaded_file


def compress_chat_image(uploaded_file, max_size=(800, 800), quality=80):
    """
    Compress chat images to smaller size for faster loading
    
    Args:
        uploaded_file: Django UploadedFile object
        max_size: Tuple of (max_width, max_height)
        quality: JPEG quality (1-100)
    
    Returns:
        Compressed InMemoryUploadedFile
    """
    return compress_image(uploaded_file, max_size=max_size, quality=quality)


def compress_profile_picture(uploaded_file, max_size=(400, 400), quality=90):
    """
    Compress profile pictures to square format
    
    Args:
        uploaded_file: Django UploadedFile object
        max_size: Tuple of (max_width, max_height)
        quality: JPEG quality (1-100)
    
    Returns:
        Compressed InMemoryUploadedFile
    """
    try:
        img = Image.open(uploaded_file)
        
        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # Crop to square (center crop)
        width, height = img.size
        min_dimension = min(width, height)
        left = (width - min_dimension) // 2
        top = (height - min_dimension) // 2
        right = left + min_dimension
        bottom = top + min_dimension
        img = img.crop((left, top, right, bottom))
        
        # Resize to target size
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Save to BytesIO
        output = BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        output.seek(0)
        
        # Create new InMemoryUploadedFile
        compressed_file = InMemoryUploadedFile(
            output,
            'ImageField',
            uploaded_file.name,
            'image/jpeg',
            sys.getsizeof(output),
            None
        )
        
        return compressed_file
    
    except Exception as e:
        print(f"Profile picture compression failed: {e}")
        return uploaded_file


def check_pending_ratings(user):
    """
    Check if user has any completed tasks that they haven't rated yet.
    Returns: QuerySet of unrated tasks
    """
    from .models import Task, Rating
    from django.db.models import Q
    
    # 1. Get all completed tasks where user was poster OR doer
    completed_tasks = Task.objects.filter(
        Q(poster=user) | Q(doer=user),
        status='completed'
    )
    
    # 2. Exclude tasks where this user has already submitted a rating
    # We use exclude() with the reverse relationship 'ratings'
    # 'ratings__rater' checks for Rating objects linked to the task where rater is the user
    pending_tasks = completed_tasks.exclude(ratings__rater=user)
    
    return pending_tasks
