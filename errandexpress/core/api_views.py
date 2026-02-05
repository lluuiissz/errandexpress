"""
API Views for Prioritization System
Provides endpoints for prioritized task listing, auto-assignment, and scheduling
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Q
from decimal import Decimal
import json

from core.models import Task, User, TaskApplication
from core.services import PrioritizationService


@login_required
@require_http_methods(["GET"])
def api_get_prioritized_tasks(request):
    """
    GET /api/tasks/prioritized/
    
    Returns prioritized task list for the current user
    Includes score breakdown for transparency
    
    Query Parameters:
    - limit: Number of tasks to return (default: 20)
    - offset: Pagination offset (default: 0)
    - category: Filter by category
    - min_price: Minimum price filter
    - max_price: Maximum price filter
    """
    try:
        user = request.user
        
        # Only doers can get prioritized tasks
        if user.role not in ['task_doer', 'admin']:
            return JsonResponse({
                'error': 'Only task doers can access prioritized tasks'
            }, status=403)
        
        # Get query parameters
        limit = int(request.GET.get('limit', 20))
        offset = int(request.GET.get('offset', 0))
        category = request.GET.get('category', None)
        min_price = request.GET.get('min_price', None)
        max_price = request.GET.get('max_price', None)
        
        # Get base tasks (open tasks, excluding user's own)
        tasks = Task.objects.filter(
            status='open'
        ).exclude(
            poster=user
        ).select_related('poster')
        
        # Apply filters
        if category:
            tasks = tasks.filter(category=category)
        if min_price:
            tasks = tasks.filter(price__gte=Decimal(min_price))
        if max_price:
            tasks = tasks.filter(price__lte=Decimal(max_price))
        
        # Apply prioritization
        prioritized_tasks = PrioritizationService.get_prioritized_tasks(tasks, user)
        
        # Get total count before pagination
        total_count = prioritized_tasks.count()
        
        # Apply pagination
        paginated_tasks = prioritized_tasks[offset:offset + limit]
        
        # Build response
        tasks_data = []
        for task in paginated_tasks:
            # Get score breakdown for this task
            breakdown = PrioritizationService.get_score_breakdown(task, user)
            
            tasks_data.append({
                'id': str(task.id),
                'title': task.title,
                'description': task.description,
                'category': task.category,
                'price': float(task.price),
                'deadline': task.deadline.isoformat(),
                'location': task.location,
                'campus_location': task.campus_location,
                'priority_level': task.priority_level,
                'poster': {
                    'id': str(task.poster.id),
                    'fullname': task.poster.fullname,
                    'campus_location': task.poster.campus_location,
                },
                'time_window': {
                    'start': task.time_window_start.isoformat() if task.time_window_start else None,
                    'end': task.time_window_end.isoformat() if task.time_window_end else None,
                    'flexible': task.flexible_timing,
                },
                'score': breakdown,
                'created_at': task.created_at.isoformat(),
            })
        
        return JsonResponse({
            'success': True,
            'total_count': total_count,
            'limit': limit,
            'offset': offset,
            'tasks': tasks_data,
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def api_auto_assign_task(request):
    """
    POST /api/tasks/auto-assign/
    
    Automatically assign the best-matching doer to a task
    
    Request Body:
    {
        "task_id": "uuid"
    }
    
    Response:
    {
        "success": true,
        "task_id": "uuid",
        "assigned_doer": {
            "id": "uuid",
            "fullname": "John Doe",
            "score": 8.5
        }
    }
    """
    try:
        user = request.user
        
        # Only task posters can auto-assign
        if user.role not in ['task_poster', 'admin']:
            return JsonResponse({
                'error': 'Only task posters can auto-assign tasks'
            }, status=403)
        
        # Parse request body
        data = json.loads(request.body)
        task_id = data.get('task_id')
        
        if not task_id:
            return JsonResponse({
                'error': 'task_id is required'
            }, status=400)
        
        # Get the task
        try:
            task = Task.objects.get(id=task_id, poster=user, status='open')
        except Task.DoesNotExist:
            return JsonResponse({
                'error': 'Task not found or not owned by you'
            }, status=404)
        
        # Get all available doers
        doers = User.objects.filter(
            role='task_doer',
            is_active=True
        ).exclude(id=user.id)
        
        # Score each doer for this task
        best_doer = None
        best_score = 0
        
        for doer in doers:
            breakdown = PrioritizationService.get_score_breakdown(task, doer)
            score = breakdown['total_score']
            
            if score > best_score:
                best_score = score
                best_doer = doer
        
        if not best_doer:
            return JsonResponse({
                'error': 'No suitable doer found'
            }, status=404)
        
        # Assign the task
        task.doer = best_doer
        task.status = 'in_progress'
        task.accepted_at = timezone.now()
        task.save()
        
        # Create notification (if notification system exists)
        # TODO: Send notification to doer
        
        return JsonResponse({
            'success': True,
            'task_id': str(task.id),
            'assigned_doer': {
                'id': str(best_doer.id),
                'fullname': best_doer.fullname,
                'campus_location': best_doer.campus_location,
                'score': best_score,
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON in request body'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def api_get_scheduled_tasks(request):
    """
    GET /api/tasks/schedule/
    
    Get user's scheduled tasks with conflict detection
    
    Query Parameters:
    - start_date: Filter tasks from this date (ISO format)
    - end_date: Filter tasks until this date (ISO format)
    
    Response includes:
    - Scheduled tasks
    - Conflict warnings
    - Optimal schedule suggestions
    """
    try:
        user = request.user
        
        # Get query parameters
        start_date = request.GET.get('start_date', None)
        end_date = request.GET.get('end_date', None)
        
        # Get user's tasks (both posted and assigned)
        if user.role == 'task_poster':
            tasks = Task.objects.filter(poster=user)
        elif user.role == 'task_doer':
            tasks = Task.objects.filter(doer=user)
        else:
            tasks = Task.objects.filter(
                Q(poster=user) | Q(doer=user)
            )
        
        # Filter by date range
        if start_date:
            tasks = tasks.filter(time_window_start__gte=start_date)
        if end_date:
            tasks = tasks.filter(time_window_end__lte=end_date)
        
        # Only get tasks with time windows
        tasks = tasks.filter(
            time_window_start__isnull=False
        ).order_by('time_window_start')
        
        # Detect conflicts
        conflicts = []
        tasks_list = list(tasks)
        
        for i, task1 in enumerate(tasks_list):
            for task2 in tasks_list[i+1:]:
                # Check if time windows overlap
                if (task1.time_window_start <= task2.time_window_end and
                    task1.time_window_end >= task2.time_window_start):
                    conflicts.append({
                        'task1_id': str(task1.id),
                        'task1_title': task1.title,
                        'task2_id': str(task2.id),
                        'task2_title': task2.title,
                        'overlap_start': max(task1.time_window_start, task2.time_window_start).isoformat(),
                        'overlap_end': min(task1.time_window_end, task2.time_window_end).isoformat(),
                    })
        
        # Build response
        tasks_data = []
        for task in tasks:
            tasks_data.append({
                'id': str(task.id),
                'title': task.title,
                'status': task.status,
                'priority_level': task.priority_level,
                'time_window': {
                    'start': task.time_window_start.isoformat(),
                    'end': task.time_window_end.isoformat(),
                    'flexible': task.flexible_timing,
                },
                'deadline': task.deadline.isoformat(),
                'role': 'poster' if task.poster == user else 'doer',
            })
        
        return JsonResponse({
            'success': True,
            'total_tasks': len(tasks_data),
            'tasks': tasks_data,
            'conflicts': conflicts,
            'has_conflicts': len(conflicts) > 0,
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def api_reschedule_task(request):
    """
    POST /api/tasks/reschedule/
    
    Reschedule a task to avoid conflicts
    
    Request Body:
    {
        "task_id": "uuid",
        "new_start": "2026-02-04T10:00:00",
        "new_end": "2026-02-04T12:00:00"
    }
    """
    try:
        user = request.user
        
        # Parse request body
        data = json.loads(request.body)
        task_id = data.get('task_id')
        new_start = data.get('new_start')
        new_end = data.get('new_end')
        
        if not all([task_id, new_start, new_end]):
            return JsonResponse({
                'error': 'task_id, new_start, and new_end are required'
            }, status=400)
        
        # Get the task
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return JsonResponse({
                'error': 'Task not found'
            }, status=404)
        
        # Check authorization
        if task.poster != user and task.doer != user:
            return JsonResponse({
                'error': 'You are not authorized to reschedule this task'
            }, status=403)
        
        # Parse new times
        from dateutil import parser
        new_start_dt = parser.parse(new_start)
        new_end_dt = parser.parse(new_end)
        
        # Validate new time window
        if new_start_dt >= new_end_dt:
            return JsonResponse({
                'error': 'Start time must be before end time'
            }, status=400)
        
        # Update task
        task.time_window_start = new_start_dt
        task.time_window_end = new_end_dt
        task.save()
        
        return JsonResponse({
            'success': True,
            'task_id': str(task.id),
            'new_time_window': {
                'start': task.time_window_start.isoformat(),
                'end': task.time_window_end.isoformat(),
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON in request body'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)
