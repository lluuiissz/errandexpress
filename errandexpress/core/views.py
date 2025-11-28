# core/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import login as django_login, logout as django_logout
from django.db import transaction
from django.db.models import (
    Q,
    Avg,
    Count,
    Case,
    When,
    IntegerField,
    F,
    Subquery,
    OuterRef,
    DecimalField,
    Value,
    ExpressionWrapper,
)
from django.db.models.functions import Coalesce
from decimal import Decimal
from django.http import JsonResponse
from django.utils import timezone
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .supabase_client import supabase
from .models import User, Task, TaskApplication, StudentSkill, Message, Rating, Report, Notification, Payment
from .forms import TaskForm, TaskApplicationForm, TaskFilterForm, SkillValidationForm, MessageForm, RatingForm, ReportForm
from .utils import compress_image, compress_chat_image, compress_profile_picture
import logging
import json
import base64
import requests
import traceback
import hmac
import hashlib

logger = logging.getLogger(__name__)


# ==================== SMART ALGORITHMS ====================

def get_pending_rating_obligations(user):
    """
    Check if user has pending rating obligations that must be completed.
    
    Returns: {
        'has_obligations': bool,
        'pending_tasks': [Task objects],
        'message': str,
        'is_blocked': bool
    }
    """
    from .models import Task, Rating, Payment
    
    pending_tasks = []
    
    # Get completed tasks where user is the poster and hasn't rated the doer
    completed_tasks = Task.objects.filter(
        poster=user,
        status='completed',
        doer__isnull=False
    ).select_related('doer')
    
    for task in completed_tasks:
        # Check if poster already rated the doer
        already_rated = Rating.objects.filter(
            task=task,
            rater=user,
            rated=task.doer
        ).exists()
        
        if not already_rated:
            # Check payment requirements
            chat_unlocked = task.chat_unlocked
            
            # For online payment: also check if task doer was paid
            if task.payment_method == 'online':
                doer_paid = Payment.objects.filter(
                    task=task,
                    payer=user,
                    receiver=task.doer,
                    status='confirmed'
                ).exists()
                
                # If chat not unlocked OR doer not paid, it's a pending obligation
                if not chat_unlocked or not doer_paid:
                    pending_tasks.append({
                        'task': task,
                        'reason': 'payment_required',
                        'needs_system_fee': not chat_unlocked,
                        'needs_doer_payment': not doer_paid,
                        'payment_method': 'online'
                    })
            else:
                # For COD: only check if chat is unlocked
                if not chat_unlocked:
                    pending_tasks.append({
                        'task': task,
                        'reason': 'payment_required',
                        'needs_system_fee': True,
                        'needs_doer_payment': False,
                        'payment_method': 'cod'
                    })
    
    has_obligations = len(pending_tasks) > 0
    is_blocked = has_obligations  # User is blocked if they have pending obligations
    
    if has_obligations:
        if len(pending_tasks) == 1:
            task_info = pending_tasks[0]
            if task_info['payment_method'] == 'online':
                if task_info['needs_system_fee'] and task_info['needs_doer_payment']:
                    message = f"⚠️ You must pay the ₱2 system fee AND pay the task doer for '{task_info['task'].title}' before rating."
                elif task_info['needs_system_fee']:
                    message = f"⚠️ You must pay the ₱2 system fee for '{task_info['task'].title}' before rating."
                else:
                    message = f"⚠️ You must pay the task doer for '{task_info['task'].title}' before rating."
            else:
                message = f"⚠️ You must pay the ₱2 system fee for '{task_info['task'].title}' before rating."
        else:
            message = f"⚠️ You have {len(pending_tasks)} task(s) with pending rating obligations. Complete payments and ratings to continue."
    else:
        message = ""
    
    return {
        'has_obligations': has_obligations,
        'pending_tasks': pending_tasks,
        'message': message,
        'is_blocked': is_blocked,
        'count': len(pending_tasks)
    }


def calculate_assignment_score(task, agent):
    """
    Calculate assignment score for an agent based on:
    - Skill match (0-100)
    - Agent availability (0-100)
    - Agent rating (0-100)
    - Workload balance (0-100)
    """
    from .models import StudentSkill, TaskAssignment
    
    skill_match = 0
    availability = 100  # Default: available
    rating = agent.avg_rating * 10 if agent.avg_rating else 0  # Convert to 0-100
    
    # Calculate skill match
    if task.category in ['typing', 'powerpoint', 'graphics']:
        user_skills = StudentSkill.objects.filter(
            student=agent,
            status='verified',
            skill_name=task.category
        ).exists()
        skill_match = 100 if user_skills else 0
    else:  # microtask
        skill_match = 100 if agent.doer_type in ['microtasker', 'both'] else 0
    
    # Calculate workload balance (fewer active tasks = higher score)
    active_assignments = TaskAssignment.objects.filter(
        agent=agent,
        status__in=['assigned', 'in_progress']
    ).count()
    workload_score = max(0, 100 - (active_assignments * 10))
    
    # Calculate total score (weighted average)
    total_score = (
        (skill_match * 0.4) +
        (availability * 0.2) +
        (rating * 0.25) +
        (workload_score * 0.15)
    )
    
    return {
        'skill_match': skill_match,
        'availability': availability,
        'rating': rating,
        'workload': workload_score,
        'total': round(total_score, 2)
    }


def reconcile_payments():
    """
    Reconcile pending payments with PayMongo
    Checks for payments that should be confirmed but aren't
    """
    from .models import Payment, SystemCommission
    
    try:
        # Find payments pending for more than 1 hour
        one_hour_ago = timezone.now() - timedelta(hours=1)
        pending_payments = Payment.objects.filter(
            status='pending',
            created_at__lt=one_hour_ago,
            paymongo_payment_id__isnull=False
        )
        
        reconciled_count = 0
        for payment in pending_payments:
            try:
                # Verify payment with PayMongo
                from .paymongo import PayMongoClient
                client = PayMongoClient()
                payment_intent = client.retrieve_payment_intent(payment.paymongo_payment_id)
                
                if payment_intent:
                    status = payment_intent['data']['attributes']['status']
                    if status == 'succeeded':
                        payment.status = 'confirmed'
                        payment.confirmed_at = timezone.now()
                        payment.save()
                        reconciled_count += 1
                        logger.info(f"Payment {payment.id} reconciled: {status}")
                        
            except Exception as e:
                logger.error(f"Error reconciling payment {payment.id}: {str(e)}")
        
        logger.info(f"Payment reconciliation complete: {reconciled_count} payments updated")
        return reconciled_count
        
    except Exception as e:
        logger.error(f"Payment reconciliation error: {str(e)}")
        return 0


def auto_assign_task(task, criteria=None):
    """
    Automatically assign a task to the best matching agent
    Criteria: skills, availability, rating, workload
    """
    from .models import TaskAssignment, StudentSkill
    
    try:
        # Get available agents (task doers)
        available_agents = User.objects.filter(
            role='task_doer',
            is_active=True,
            is_banned=False
        )
        
        # Filter by skill match if needed
        if task.category in ['typing', 'powerpoint', 'graphics']:
            skilled_agents = StudentSkill.objects.filter(
                status='verified',
                skill_name=task.category
            ).values_list('student_id', flat=True)
            available_agents = available_agents.filter(id__in=skilled_agents)
        else:
            # Microtask: allow microtaskers and 'both' type
            available_agents = available_agents.filter(
                doer_type__in=['microtasker', 'both']
            )
        
        if not available_agents.exists():
            logger.warning(f"No available agents for task {task.id}")
            return None
        
        # Score all available agents
        best_agent = None
        best_score = -1
        
        for agent in available_agents:
            scores = calculate_assignment_score(task, agent)
            if scores['total'] > best_score:
                best_score = scores['total']
                best_agent = agent
        
        if best_agent:
            # Create assignment
            assignment = TaskAssignment.objects.create(
                task=task,
                agent=best_agent,
                assigned_by=task.poster,
                status='assigned',
                assignment_method='automatic',
                skill_match_score=scores['skill_match'],
                availability_score=scores['availability'],
                rating_score=scores['rating'],
                workload_score=scores['workload'],
                total_match_score=scores['total'],
                assignment_notes=f"Auto-assigned based on skill match, rating, and availability"
            )
            
            # Send notification to agent
            Notification.objects.create(
                user=best_agent,
                type='task_assigned',
                title='🎯 Task Assigned to You',
                message=f'You have been assigned to "{task.title}" by {task.poster.fullname}',
                related_task=task
            )
            
            logger.info(f"Task {task.id} auto-assigned to {best_agent.fullname} with score {best_score}")
            return assignment
        
        return None
        
    except Exception as e:
        logger.error(f"Error auto-assigning task {task.id}: {str(e)}")
        return None


def get_matched_tasks_for_user(user):
    """
    🎯 SMART TASK MATCHING ALGORITHM
    Shows tasks based on user's doer_type and validated skills
    
    3-MINUTE APPLICATION WINDOW:
    - When first application arrives, start 3-minute timer
    - During 3 minutes: Task stays visible for other doers to apply
    - After 3 minutes: Hide task ONLY if:
      * Task poster chose a doer, OR
      * Only 1 applicant (task taken)
    - If multiple applicants after 3 min: Keep showing task
    """
    if user.role not in ['task_doer', 'admin']:
        return Task.objects.none()
    
    # Get user's validated skills
    user_skills = list(StudentSkill.objects.filter(
        student=user, 
        status='verified'
    ).values_list('skill_name', flat=True))
    
    # Base query for open tasks
    base_tasks = Task.objects.filter(status='open').select_related('poster')
    
    # 🧹 FILTER OUT TASKS THAT SHOULD BE HIDDEN (3-minute window logic)
    # ✅ OPTIMIZED: Use database queries instead of Python loop
    now = timezone.now()
    three_minutes_ago = now - timezone.timedelta(minutes=3)
    
    # Find tasks to exclude using database queries (no N+1!)
    from django.db.models import Min, Count
    
    # Tasks with applications that have passed 3-minute window
    tasks_with_old_apps = base_tasks.filter(
        applications__status='pending',
        applications__first_application_time__lte=three_minutes_ago
    ).filter(
        Q(doer__isnull=False)  # Doer already chosen
    ).distinct().values_list('id', flat=True)
    
    # Tasks with only 1 application that passed 3-minute window
    tasks_with_single_app = base_tasks.filter(
        applications__status='pending',
        applications__first_application_time__lte=three_minutes_ago
    ).annotate(
        app_count=Count('applications', filter=Q(applications__status='pending'))
    ).filter(
        app_count=1
    ).distinct().values_list('id', flat=True)
    
    # Combine both exclusion lists
    tasks_to_exclude = list(tasks_with_old_apps) + list(tasks_with_single_app)
    
    # Exclude hidden tasks
    base_tasks = base_tasks.exclude(id__in=tasks_to_exclude)
    
    if user.doer_type == 'microtasker':
        # Show all microtasks (simple tasks that don't require special skills)
        tasks = base_tasks.filter(
            Q(category='microtask') | 
            Q(tags__icontains='microtask')
        )
    elif user.doer_type == 'skilled':
        # Show only tasks that match validated skills
        if not user_skills:
            # No validated skills = no skilled tasks
            tasks = Task.objects.none()
        else:
            skill_queries = Q()
            for skill in user_skills:
                if skill == 'typing':
                    skill_queries |= Q(category='typing') | Q(tags__icontains='typing')
                elif skill == 'powerpoint':
                    skill_queries |= Q(category='powerpoint') | Q(tags__icontains='powerpoint')
                elif skill == 'graphics':
                    skill_queries |= Q(category='graphics') | Q(tags__icontains='graphics')
            
            tasks = base_tasks.filter(skill_queries)
    else:  # both
        # Show microtasks + skilled tasks that match user's skills
        microtask_query = Q(category='microtask') | Q(tags__icontains='microtask')
        
        skill_queries = Q()
        for skill in user_skills:
            if skill == 'typing':
                skill_queries |= Q(category='typing') | Q(tags__icontains='typing')
            elif skill == 'powerpoint':
                skill_queries |= Q(category='powerpoint') | Q(tags__icontains='powerpoint')
            elif skill == 'graphics':
                skill_queries |= Q(category='graphics') | Q(tags__icontains='graphics')
        
        tasks = base_tasks.filter(microtask_query | skill_queries)
    
    # 🧠 SMART RANKING ALGORITHM (FIXED - Real-time Poster Ratings)
    # Priority = (Skill Match × 3) + (Poster Rating × 2) + (Urgency × 1)
    
    # Calculate real-time poster ratings from Rating table
    poster_rating_subquery = Rating.objects.filter(
        rated=OuterRef('poster')
    ).values('rated').annotate(
        avg_rating=Avg('score')
    ).values('avg_rating')
    
    tasks = tasks.annotate(
        skill_match_score=Case(
            # Check if task matches user's skills
            *[When(Q(category='typing') | Q(tags__icontains='typing'), then=3) 
              for skill in user_skills if skill == 'typing'] +
            [When(Q(category='powerpoint') | Q(tags__icontains='powerpoint'), then=3) 
             for skill in user_skills if skill == 'powerpoint'] +
            [When(Q(category='graphics') | Q(tags__icontains='graphics'), then=3) 
             for skill in user_skills if skill == 'graphics_design'],
            default=0,
            output_field=IntegerField()
        ),
        urgency_score=Case(
            When(deadline__lte=timezone.now() + timezone.timedelta(days=1), then=1),
            default=0,
            output_field=IntegerField()
        ),
        # FIXED: Use real-time poster rating from Rating table instead of stale avg_rating field
        poster_rating=Coalesce(
            Subquery(poster_rating_subquery, output_field=DecimalField(max_digits=4, decimal_places=2)),
            Value(Decimal('0.00'), output_field=DecimalField(max_digits=4, decimal_places=2)),
            output_field=DecimalField(max_digits=4, decimal_places=2)
        ),
        # Calculate total priority score with consistent Decimal arithmetic
        priority_score=ExpressionWrapper(
            (F('skill_match_score') * Value(Decimal('1.00'), output_field=DecimalField(max_digits=5, decimal_places=2))) +
            (F('poster_rating') * Value(Decimal('2.00'), output_field=DecimalField(max_digits=5, decimal_places=2))) +
            (F('urgency_score') * Value(Decimal('1.00'), output_field=DecimalField(max_digits=5, decimal_places=2))),
            output_field=DecimalField(max_digits=7, decimal_places=2)
        )
    ).order_by('-priority_score', '-created_at')
    
    return tasks


def handle_task_creation_with_payment(poster, title, description, category, tags, price, payment_method, deadline, location=None, requirements=None):
    """
    💸 COMPREHENSIVE PAYMENT ALGORITHM - STEP 1: Task Creation
    Creates task and handles ₱2 system fee based on payment method
    
    LOGIC:
    - COD: commission_status = "unpaid", chat_unlocked = False
    - GCash: commission_status = "paid", chat_unlocked = True
    """
    from .models import SystemCommission
    
    # Create task record
    task = Task.objects.create(
        poster=poster,
        title=title,
        description=description,
        category=category,
        tags=tags,
        price=price,
        payment_method=payment_method,
        deadline=deadline,
        location=location,
        requirements=requirements,
        status='open',
        chat_unlocked=False  # Always start locked initially
    )
    
    # 🔹 STEP 1 LOGIC: Payment method determines initial state
    if payment_method.lower() == 'online':
        # Online Payment (GCash): ₱2 fee considered pre-paid, unlock chat immediately
        commission_status = 'paid'
        chat_unlocked = True
        paid_at = timezone.now()
        
        logger.info(f"Online payment task created - chat unlocked immediately for task {task.id}")
        
    else:  # COD
        # COD: ₱2 fee must be paid manually, keep chat locked
        commission_status = 'unpaid'
        chat_unlocked = False
        paid_at = None
        
        logger.info(f"COD task created - chat locked until ₱2 payment for task {task.id}")
    
    # Create system commission record
    SystemCommission.objects.create(
        task=task,
        payer=poster,
        amount=2.00,  # ₱2 system fee
        method=payment_method,
        status=commission_status,
        paid_at=paid_at
    )
    
    # Update task chat status
    task.chat_unlocked = chat_unlocked
    task.save()
    
    # Create notification for poster
    Notification.objects.create(
        user=poster,
        type='task_created',
        title='Task Created Successfully',
        message=f'Task "{title}" created. Chat {"unlocked" if chat_unlocked else "locked until ₱2 payment"}.',
        related_task=task
    )
    
    return task


def check_chat_access(task_id, user):
    """
    💬 CHAT LOCK / UNLOCK ALGORITHM WITH 5-MESSAGE LIMIT
    Checks if user can access chat for a specific task
    
    RULES:
    1. First 5 messages are FREE (combined from both users)
    2. After 5 messages, ₱2 system fee must be paid to continue
    3. Only poster and assigned doer can chat
    """
    try:
        task = Task.objects.select_related('poster', 'doer').get(id=task_id)
        
        # Only poster and assigned doer can chat
        if user not in [task.poster, task.doer]:
            return {'allowed': False, 'reason': 'Not authorized for this task'}
        
        # Count total messages in this task using aggregation (faster than count())
        from django.db.models import Count
        from .models import Message
        message_count = Message.objects.filter(task=task).aggregate(Count('id'))['id__count']
        
        # First 5 messages are FREE
        if message_count < 5:
            return {
                'allowed': True, 
                'reason': 'Free messages remaining',
                'messages_remaining': 5 - message_count,
                'free_tier': True
            }
        
        # After 5 messages, check if ₱2 system fee is paid
        if not task.chat_unlocked:
            return {
                'allowed': False, 
                'reason': 'You have reached the 5-message limit. Please pay ₱2 system fee to continue chatting.',
                'payment_required': True,
                'messages_used': message_count
            }
        
        # Chat is unlocked after payment
        return {
            'allowed': True, 
            'reason': 'Chat access granted (paid)',
            'messages_used': message_count,
            'paid': True
        }
        
    except Task.DoesNotExist:
        return {'allowed': False, 'reason': 'Task not found'}


def handle_task_completion_payment(task_id, poster, payment_method='gcash'):
    """
    💸 COMPREHENSIVE PAYMENT ALGORITHM - STEP 5: Task Completion Payment
    Handles main task fee payment (₱10-₱100+ etc.)
    
    FLOWS:
    A. COD: Manual confirmation by poster
    B. GCash: Automatic via PayMongo webhook
    """
    from .models import Task, Payment
    
    try:
        task = Task.objects.get(id=task_id, poster=poster)
        
        if task.status != 'in_progress':
            return {'success': False, 'error': 'Task is not in progress'}
        
        if not task.doer:
            return {'success': False, 'error': 'No doer assigned to this task'}
        
        # Check if payment already exists
        existing_payment = Payment.objects.filter(task=task).first()
        if existing_payment and existing_payment.status == 'paid':
            return {'success': False, 'error': 'Task payment already completed'}
        
        # 🔹 STEP 5A: COD Flow (Manual Confirmation)
        if payment_method.lower() == 'cod':
            # Create payment record as pending manual confirmation
            payment = Payment.objects.create(
                task=task,
                poster=poster,
                doer=task.doer,
                amount=task.price,
                method='cod',
                status='pending_confirmation',  # Waiting for poster to confirm
                description=f'Task payment for "{task.title}"'
            )
            
            # Task remains in_progress until manual confirmation
            logger.info(f"COD payment created for task {task_id} - awaiting manual confirmation")
            
            # Notify doer that task is completed, awaiting payment
            Notification.objects.create(
                user=task.doer,
                type='task_completed',
                title='Task Completed - Awaiting Payment',
                message=f'Task "{task.title}" completed. Awaiting COD payment confirmation from poster.',
                related_task=task
            )
            
            return {
                'success': True, 
                'payment_id': payment.id,
                'status': 'pending_confirmation',
                'message': 'Task completed. Please confirm COD payment when received.'
            }
        
        # 🔹 STEP 5B: GCash Flow (Automatic via PayMongo)
        elif payment_method.lower() == 'gcash':
            # Create payment record as pending online payment
            payment = Payment.objects.create(
                task=task,
                poster=poster,
                doer=task.doer,
                amount=task.price,
                method='gcash',
                status='pending_payment',  # Waiting for PayMongo confirmation
                description=f'Task payment for "{task.title}"'
            )
            
            logger.info(f"GCash payment initiated for task {task_id} - amount: ₱{task.price}")
            
            return {
                'success': True,
                'payment_id': payment.id,
                'status': 'pending_payment',
                'amount': float(task.price),
                'message': 'Proceed to GCash payment'
            }
        
        else:
            return {'success': False, 'error': 'Invalid payment method'}
            
    except Task.DoesNotExist:
        return {'success': False, 'error': 'Task not found'}
    except Exception as e:
        logger.error(f"Task completion payment error: {str(e)}")
        return {'success': False, 'error': str(e)}


def confirm_cod_payment(payment_id, poster):
    """
    💵 COD Manual Confirmation - STEP 5A Completion
    Poster manually confirms COD payment received
    """
    from .models import Payment
    
    try:
        payment = Payment.objects.get(id=payment_id, poster=poster, method='cod')
        
        if payment.status == 'paid':
            return {'success': False, 'error': 'Payment already confirmed'}
        
        # Mark payment as paid
        payment.status = 'paid'
        payment.paid_at = timezone.now()
        payment.save()
        
        # Complete the task
        task = payment.task
        task.status = 'completed'
        task.completed_at = timezone.now()
        task.save()
        
        # Notify doer of payment confirmation
        Notification.objects.create(
            user=payment.doer,
            type='payment_confirmed',
            title='Payment Confirmed! 💰',
            message=f'COD payment confirmed for task "{task.title}". Task completed!',
            related_task=task
        )
        
        # Notify both users to rate each other
        Notification.objects.create(
            user=poster,
            type='rate_reminder',
            title='Please Rate Your Doer',
            message=f'Task "{task.title}" completed. Please rate {payment.doer.fullname}.',
            related_task=task
        )
        
        Notification.objects.create(
            user=payment.doer,
            type='rate_reminder',
            title='Please Rate Your Poster',
            message=f'Task "{task.title}" completed. Please rate {poster.fullname}.',
            related_task=task
        )
        
        logger.info(f"COD payment confirmed for task {task.id} - task completed")
        
        return {
            'success': True,
            'message': 'Payment confirmed successfully. Task completed!',
            'task_status': 'completed'
        }
        
    except Payment.DoesNotExist:
        return {'success': False, 'error': 'Payment not found'}
    except Exception as e:
        logger.error(f"COD confirmation error: {str(e)}")
        return {'success': False, 'error': str(e)}

@csrf_exempt
def health_check(request):
    """Health check endpoint for monitoring and load balancers"""
    try:
        # Check database connectivity
        User.objects.count()
        
        # Check cache connectivity (if Redis is configured)
        from django.core.cache import cache
        cache.set('health_check', 'ok', 10)
        
        return JsonResponse({
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'database': 'connected',
            'cache': 'connected'
        }, status=200)
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JsonResponse({
            'status': 'unhealthy',
            'timestamp': timezone.now().isoformat(),
            'error': str(e)
        }, status=503)


def home(request):
    """Redesigned homepage with better navigation and organization"""
    context = {
        'total_tasks': Task.objects.filter(status='completed').count(),
        'total_users': User.objects.filter(is_active=True).count(),
        'avg_rating': Rating.objects.aggregate(Avg('score'))['score__avg'] or 4.9,
    }
    return render(request, "home_modern.html", context)

def terms_of_service(request):
    """Terms of Service page"""
    return render(request, "terms_of_service.html")

def privacy_policy(request):
    """Privacy Policy page"""
    return render(request, "privacy_policy.html")

def signup_view(request):
    if request.method == "POST":
        fullname = request.POST.get("fullname")
        email = request.POST.get("email")
        password = request.POST.get("password")
        role = request.POST.get("role", "task_doer")
        doer_type = request.POST.get("doer_type", "")
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "An account with this email already exists.")
            return redirect("signup")
        
        try:
            # For now, create Django user directly (bypass Supabase temporarily)
            # TODO: Re-enable Supabase integration once response format is resolved
            
            import uuid
            django_user = User.objects.create_user(
                id=uuid.uuid4(),
                username=email,
                email=email,
                password=password,
                fullname=fullname,
                role=role,
                doer_type=doer_type if role == "task_doer" else "",
                is_active=True
            )
            
            logger.info(f"Created Django user {django_user.id} for email {email}")
            messages.success(request, "Account created successfully! You can now log in.")
            return redirect("login")
            
            # Supabase integration (temporarily disabled)
            """
            result = supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "fullname": fullname, 
                        "role": role,
                        "doer_type": doer_type if role == "task_doer" else ""
                    }
                }
            })
            
            # Handle Supabase AuthResponse object
            if hasattr(result, 'user') and result.user:
                supabase_user = result.user
            elif hasattr(result, 'data') and result.data and hasattr(result.data, 'user'):
                supabase_user = result.data.user
            else:
                # Check for error in the response
                error_msg = "Failed to create account."
                if hasattr(result, 'error') and result.error:
                    error_msg = str(result.error)
                elif hasattr(result, 'data') and hasattr(result.data, 'error') and result.data.error:
                    error_msg = str(result.data.error)
                messages.error(request, error_msg)
                return redirect("signup")
            
            if not supabase_user:
                messages.error(request, "Failed to create account. Please try again.")
                return redirect("signup")
            
            # Create corresponding Django User
            with transaction.atomic():
                # Handle different user object structures
                user_id = supabase_user.id if hasattr(supabase_user, 'id') else supabase_user['id']
                user_email = supabase_user.email if hasattr(supabase_user, 'email') else supabase_user['email']
                
                django_user, created = User.objects.get_or_create(
                    id=user_id,
                    defaults={
                        'username': user_email,  # Use email as username
                        'email': user_email,
                        'fullname': fullname,
                        'role': role,
                        'doer_type': doer_type if role == "task_doer" else "",
                        'is_active': False,  # Will be activated when email is confirmed
                    }
                )
                
                if created:
                    logger.info(f"Created Django user for Supabase user {user_id}")
                
            messages.success(request, "Account created successfully! Please check your email for confirmation.")
            return redirect("login")
            """
            
        except Exception as e:
            logger.error(f"Signup error: {str(e)}")
            messages.error(request, f"An error occurred during signup: {str(e)}")
            return redirect("signup")
    
    return render(request, "signup_modern.html")

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        try:
            # Use Django authentication for now (bypass Supabase temporarily)
            # TODO: Re-enable Supabase integration once response format is resolved
            
            from django.contrib.auth import authenticate
            
            # Try to find user by email (since we use email as username)
            try:
                django_user = User.objects.get(email=email)
                # Authenticate using the username (which is the email)
                authenticated_user = authenticate(request, username=django_user.username, password=password)
                
                if authenticated_user:
                    django_login(request, authenticated_user)
                    messages.success(request, f"Welcome back, {authenticated_user.fullname}!")
                    return redirect("dashboard")
                else:
                    messages.error(request, "Invalid email or password.")
                    return redirect("login")
                    
            except User.DoesNotExist:
                messages.error(request, "No account found with this email address.")
                return redirect("login")
            
            # Supabase integration (temporarily disabled)
            """
            # Authenticate with Supabase
            result = supabase.auth.sign_in_with_password({
                "email": email, 
                "password": password
            })
            
            # Handle Supabase AuthResponse object
            if hasattr(result, 'user') and result.user:
                supabase_user = result.user
            elif hasattr(result, 'data') and result.data and hasattr(result.data, 'user'):
                supabase_user = result.data.user
            else:
                # Check for error in the response
                error_msg = "Login failed. Please try again."
                if hasattr(result, 'error') and result.error:
                    error_msg = str(result.error)
                elif hasattr(result, 'data') and hasattr(result.data, 'error') and result.data.error:
                    error_msg = str(result.data.error)
                messages.error(request, error_msg)
                return redirect("login")
            
            if not supabase_user:
                messages.error(request, "Login failed. Please try again.")
                return redirect("login")
            
            # Get or create corresponding Django user
            try:
                # Handle different user object structures
                user_id = supabase_user.id if hasattr(supabase_user, 'id') else supabase_user['id']
                user_email = supabase_user.email if hasattr(supabase_user, 'email') else supabase_user['email']
                
                django_user = User.objects.get(id=user_id)
                
                # Update user info from Supabase metadata
                user_metadata = supabase_user.user_metadata if hasattr(supabase_user, 'user_metadata') else supabase_user.get('user_metadata', {})
                if user_metadata:
                    if hasattr(user_metadata, 'get'):
                        django_user.fullname = user_metadata.get('fullname', django_user.fullname)
                        django_user.role = user_metadata.get('role', django_user.role)
                        django_user.doer_type = user_metadata.get('doer_type', django_user.doer_type)
                    else:
                        # Handle if user_metadata is an object with attributes
                        django_user.fullname = getattr(user_metadata, 'fullname', django_user.fullname)
                        django_user.role = getattr(user_metadata, 'role', django_user.role)
                        django_user.doer_type = getattr(user_metadata, 'doer_type', django_user.doer_type)
                    django_user.is_active = True  # Activate user on successful login
                    django_user.save()
                
            except User.DoesNotExist:
                # Create Django user if it doesn't exist
                user_metadata = supabase_user.user_metadata if hasattr(supabase_user, 'user_metadata') else supabase_user.get('user_metadata', {})
                
                # Extract metadata safely
                if hasattr(user_metadata, 'get'):
                    fullname = user_metadata.get('fullname', '')
                    role = user_metadata.get('role', 'task_doer')
                    doer_type = user_metadata.get('doer_type', '')
                else:
                    fullname = getattr(user_metadata, 'fullname', '')
                    role = getattr(user_metadata, 'role', 'task_doer')
                    doer_type = getattr(user_metadata, 'doer_type', '')
                
                django_user = User.objects.create(
                    id=user_id,
                    username=user_email,
                    email=user_email,
                    fullname=fullname,
                    role=role,
                    doer_type=doer_type,
                    is_active=True
                )
                logger.info(f"Created Django user during login for {user_id}")
            
            # Log the user into Django
            django_login(request, django_user)
            
            # Store additional session data
            request.session['supabase_user_id'] = user_id
            request.session['user_metadata'] = user_metadata if hasattr(user_metadata, 'get') else {}
            
            messages.success(request, f"Welcome back, {django_user.fullname}!")
            return redirect("dashboard")
            """
            
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            messages.error(request, f"An error occurred during login: {str(e)}")
            return redirect("login")
    
    return render(request, "login_modern.html")

def dashboard(request):
    # Check if user is authenticated
    if not request.user.is_authenticated:
        messages.info(request, "Please log in to access your dashboard.")
        return redirect("login")
    
    # Get user data
    user = request.user
    from datetime import datetime, timedelta
    from django.db.models import Q, Avg, Sum, Count
    from django.utils import timezone
    
    # ✅ NEW: Check for pending rating obligations (SYSTEM BLOCK)
    rating_obligations = get_pending_rating_obligations(user)
    if rating_obligations['is_blocked']:
        # User is blocked from using system until they complete ratings
        messages.error(request, rating_obligations['message'])
        return render(request, 'blocked_pending_ratings.html', {
            'pending_tasks': rating_obligations['pending_tasks'],
            'message': rating_obligations['message'],
            'count': rating_obligations['count']
        })
    
    # Current month calculations
    current_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    if user.role == 'task_poster':
        # ✅ OPTIMIZED: Use aggregation for all counts (single query)
        # TASK POSTER METRICS
        all_tasks = Task.objects.filter(poster=user)
        
        # ✅ OPTIMIZED: Calculate all counts in one aggregation query
        stats = all_tasks.aggregate(
            active_count=Count('id', filter=Q(status__in=['open', 'in_progress'])),
            completed_count=Count('id', filter=Q(status='completed')),
            total_assigned=Count('id', filter=~Q(status='open')),
            monthly_spent=Sum('price', filter=Q(created_at__gte=current_month))
        )
        
        active_tasks = all_tasks.filter(status__in=['open', 'in_progress'])
        completed_tasks = all_tasks.filter(status='completed')
        
        total_spent = stats['monthly_spent'] or 0
        
        # ✅ OPTIMIZED: Calculate average completion time using database aggregation
        from django.db.models import F, ExpressionWrapper, DurationField
        completed_with_times = completed_tasks.exclude(completed_at__isnull=True, accepted_at__isnull=True)
        avg_completion_hours = 0
        if completed_with_times.exists():
            avg_duration = completed_with_times.aggregate(
                avg_time=Avg(ExpressionWrapper(F('completed_at') - F('accepted_at'), output_field=DurationField()))
            )['avg_time']
            if avg_duration:
                avg_completion_hours = avg_duration.total_seconds() / 3600
        
        # ✅ OPTIMIZED: Calculate success rate from aggregation
        total_assigned = stats['total_assigned']
        success_rate = (stats['completed_count'] / total_assigned * 100) if total_assigned > 0 else 0
        
        # ✅ OPTIMIZED: Get tasks with applications (not messages)
        pending_applications = all_tasks.filter(status='open').annotate(
            app_count=Count('applications', filter=Q(applications__status='pending'))
        ).filter(app_count__gt=0)[:5]
        
        # ✅ OPTIMIZED: Get tasks in different states with select_related
        in_progress_tasks = active_tasks.filter(status='in_progress').select_related('doer')[:5]
        awaiting_review = completed_tasks.select_related('doer')[:5]
        payment_pending = completed_tasks.select_related('doer')[:5]
        
        # ✅ OPTIMIZED: Recent tasks with select_related
        recent_tasks = all_tasks.select_related('doer').order_by('-created_at')[:5]
        
        context = {
            'user': user,
            'is_poster': True,
            # Key Metrics
            'active_tasks_count': active_tasks.count(),
            'total_spent': total_spent,
            'avg_completion_time': round(avg_completion_hours, 1),
            'success_rate': round(success_rate, 1),
            
            # Task Management
            'pending_applications': pending_applications[:5],
            'in_progress_tasks': in_progress_tasks[:5],
            'awaiting_review': awaiting_review[:5],
            'payment_pending': payment_pending[:5],
            
            # Activity
            'recent_tasks': recent_tasks,
            
            # Smart Insights (mock data for now)
            'best_posting_time': '2:00 PM - 4:00 PM',
            'avg_market_rate': 150,
            'peak_season': 'Finals Week',
        }
        
    else:
        # TASK DOER METRICS
        completed_tasks = Task.objects.filter(doer=user, status='completed')
        in_progress_tasks = Task.objects.filter(doer=user, status='in_progress')
        all_doer_tasks = Task.objects.filter(doer=user)
        
        # Calculate total earnings this month
        monthly_completed = completed_tasks.filter(completed_at__gte=current_month)
        total_earnings = monthly_completed.aggregate(total=Sum('price'))['total'] or 0
        pending_earnings = in_progress_tasks.aggregate(total=Sum('price'))['total'] or 0
        
        # Calculate success rate with proper decimal handling
        total_assigned = all_doer_tasks.count()
        success_rate = float((completed_tasks.count() / Decimal(total_assigned)) * 100) if total_assigned > 0 else 0.0
        
        # Calculate average rating
        ratings = Rating.objects.filter(task__doer=user)
        avg_rating = ratings.aggregate(avg=Avg('score'))['avg'] or 0
        
        # Get available tasks (smart matching)
        available_tasks = get_matched_tasks_for_user(user)[:10]
        
        # Get tasks where user has shown interest (sent messages)
        active_applications = Task.objects.filter(
            status='open',
            messages__sender=user
        ).distinct()[:5]
        
        # Skill validation status
        validated_skills = user.skills.filter(status='verified')
        
        context = {
            'user': user,
            'is_doer': True,
            # Key Metrics
            'tasks_completed': completed_tasks.count(),
            'total_earnings': total_earnings,
            'pending_earnings': pending_earnings,
            'success_rate': round(success_rate, 1),
            'avg_rating': round(avg_rating, 1),
            
            # Task Feed
            'recommended_tasks': available_tasks[:5],
            'high_priority_tasks': Task.objects.filter(
                status='open',
                doer__isnull=True,
                price__gte=200
            ).exclude(poster=user)[:3],
            'nearby_tasks': available_tasks[:3],  # Would use location in real implementation
            'quick_wins': Task.objects.filter(
                status='open',
                doer__isnull=True,
                price__lte=100
            ).exclude(poster=user)[:3],
            
            # Performance Tracking
            'active_applications': active_applications,
            'current_work': in_progress_tasks[:5],
            'pending_payments': completed_tasks.filter(payment__status='pending')[:5],
            
            # Skills
            'validated_skills': validated_skills,
            'skill_count': validated_skills.count(),
            
            # Earnings Insights (mock data for now)
            'weekly_goal': 1000,
            'weekly_progress': total_earnings * 4,  # Rough weekly estimate
            'weekly_progress_percentage': min(100, (total_earnings * 4 / 1000 * 100)) if total_earnings > 0 else 0,
            'best_skill': 'Typing',
            'peak_hours': '6:00 PM - 10:00 PM',
        }
    
    return render(request, "dashboard_comprehensive.html", context)

def logout_view(request):
    try:
        # Sign out from Supabase
        supabase.auth.sign_out()
    except Exception as e:
        logger.warning(f"Supabase logout error: {str(e)}")
    
    # Django logout
    django_logout(request)
    request.session.flush()
    
    messages.success(request, "You have been logged out successfully.")
    return redirect("home")


# ==================== TASK MANAGEMENT VIEWS ====================

@login_required
def create_task(request):
    """Create a new task (Task Posters only)"""
    if request.user.role != 'task_poster':
        messages.error(request, "Only Task Posters can create tasks.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            try:
                payment_method = form.cleaned_data['payment_method']
                logger.info(f"Creating task with payment_method: {payment_method}")
                
                # Use payment handler to create task with SystemCommission
                task = handle_task_creation_with_payment(
                    poster=request.user,
                    title=form.cleaned_data['title'],
                    description=form.cleaned_data['description'],
                    category=form.cleaned_data['category'],
                    tags=form.cleaned_data['tags'],
                    price=form.cleaned_data['price'],
                    payment_method=payment_method,
                    deadline=form.cleaned_data['deadline'],
                    location=form.cleaned_data.get('location', ''),
                    requirements=form.cleaned_data.get('requirements', '')
                )
                
                # Verify commission was created
                if hasattr(task, 'commission'):
                    logger.info(f"✅ Task created with commission: {task.commission.id}, status: {task.commission.status}")
                else:
                    logger.error(f"❌ Task created but NO commission found for task {task.id}")
                
                messages.success(request, f"Task '{task.title}' created successfully!")
                return redirect('task_detail', task_id=task.id)
            except Exception as e:
                logger.error(f"❌ Error creating task: {str(e)}", exc_info=True)
                messages.error(request, f"Error creating task: {str(e)}")
        else:
            # Log form errors for debugging
            logger.warning(f"Form validation failed: {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = TaskForm()
    
    return render(request, 'create_task_modern.html', {'form': form})


@login_required
def edit_task(request, task_id):
    """Edit an existing task (Task Poster only)"""
    task = get_object_or_404(Task, id=task_id)
    
    # Check authorization - only poster can edit
    if request.user != task.poster:
        messages.error(request, "You can only edit your own tasks.")
        return redirect('task_detail', task_id=task_id)
    
    # Check if task can be edited - only open tasks can be edited
    if task.status != 'open':
        messages.error(request, "You can only edit open tasks. Once work has started, editing is not allowed.")
        return redirect('task_detail', task_id=task_id)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            try:
                task = form.save(commit=False)
                task.updated_at = timezone.now()
                task.save()
                messages.success(request, f"Task '{task.title}' updated successfully!")
                return redirect('task_detail', task_id=task.id)
            except Exception as e:
                logger.error(f"Error updating task: {str(e)}", exc_info=True)
                messages.error(request, f"Error updating task: {str(e)}")
        else:
            # Log form errors for debugging
            logger.warning(f"Form validation failed: {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = TaskForm(instance=task)
    
    return render(request, 'edit_task_modern.html', {'form': form, 'task': task})


@login_required
def browse_tasks(request):
    """Browse available tasks (Task Doers) with intelligent matching"""
    if request.user.role not in ['task_doer', 'admin']:
        messages.error(request, "Only Task Doers can browse tasks.")
        return redirect('dashboard')
    
    # Get filter form
    filter_form = TaskFilterForm(request.GET)
    
    # 🎯 SMART TASK MATCHING ALGORITHM
    tasks = get_matched_tasks_for_user(request.user)
    
    # Apply filters
    if filter_form.is_valid():
        search = filter_form.cleaned_data.get('search')
        if search:
            tasks = tasks.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(tags__icontains=search)
            )
        
        category = filter_form.cleaned_data.get('category')
        if category:
            tasks = tasks.filter(category=category)
        
        min_price = filter_form.cleaned_data.get('min_price')
        if min_price:
            tasks = tasks.filter(price__gte=min_price)
        
        max_price = filter_form.cleaned_data.get('max_price')
        if max_price:
            tasks = tasks.filter(price__lte=max_price)
        
        sort_by = filter_form.cleaned_data.get('sort_by')
        if sort_by:
            tasks = tasks.order_by(sort_by)
    
    # Ensure we always have ordering for pagination
    if not tasks.query.order_by:
        tasks = tasks.order_by('-created_at')
    
    # ✅ OPTIMIZED: Cache count before pagination
    total_tasks = tasks.count()
    
    # Pagination
    paginator = Paginator(tasks, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'tasks': page_obj,
        'filter_form': filter_form,
        'total_tasks': total_tasks
    }
    
    return render(request, 'browse_tasks_modern.html', context)


@login_required
def task_detail(request, task_id):
    """View task details"""
    # ✅ OPTIMIZED: Use select_related to fetch poster and doer in one query
    task = Task.objects.select_related('poster', 'doer').get(id=task_id)
    
    # Check if user can view this task
    can_view = (
        task.poster == request.user or
        task.doer == request.user or
        request.user.role == 'admin' or
        task.status == 'open'
    )
    
    if not can_view:
        messages.error(request, "You don't have permission to view this task.")
        return redirect('dashboard')
    
    # ✅ OPTIMIZED: Paginate messages (limit to last 50)
    messages_list = Message.objects.filter(task=task).select_related('sender').order_by('-created_at')[:50]
    messages_list = list(reversed(messages_list))  # Reverse to get chronological order
    
    # Message form for participants
    message_form = None
    if task.poster == request.user or task.doer == request.user:
        message_form = MessageForm()
    
    # Check if user has already rated the other party
    already_rated_doer = False
    already_rated_poster = False
    
    if task.status == 'completed':
        if request.user == task.poster and task.doer:
            # Check if poster already rated the doer
            already_rated_doer = Rating.objects.filter(
                task=task,
                rater=request.user,
                rated=task.doer
            ).exists()
        elif request.user == task.doer:
            # Check if doer already rated the poster
            already_rated_poster = Rating.objects.filter(
                task=task,
                rater=request.user,
                rated=task.poster
            ).exists()
    
    # ✅ NEW: Check doer's application status (if they're a task doer viewing this task)
    doer_application = None
    doer_application_status = None
    if request.user.role == 'task_doer' and request.user != task.poster:
        doer_application = TaskApplication.objects.filter(
            task=task,
            doer=request.user
        ).first()
        if doer_application:
            doer_application_status = doer_application.status
    
    context = {
        'task': task,
        'messages': messages_list,
        'message_form': message_form,
        'can_accept': (
            request.user.role == 'task_doer' and 
            task.status == 'open' and 
            task.poster != request.user
        ),
        'can_complete': (
            task.doer == request.user and 
            task.status == 'in_progress'
        ),
        'can_confirm': (
            task.poster == request.user and 
            task.status == 'completed'
        ),
        'already_rated_doer': already_rated_doer,
        'already_rated_poster': already_rated_poster,
        'doer_application_status': doer_application_status,  # ✅ NEW
    }
    
    return render(request, 'task_detail_modern.html', context)


@login_required
def accept_task(request, task_id):
    """
    ✅ DISABLED: Direct task acceptance removed
    
    Task doers must now apply through the application system.
    Task posters must accept the application.
    This ensures proper vetting before work begins.
    """
    task = get_object_or_404(Task, id=task_id)
    
    if request.user.role != 'task_doer':
        messages.error(request, "Only Task Doers can accept tasks.")
        return redirect('task_detail', task_id=task_id)
    
    # ✅ NEW: Check if user already applied
    existing_app = TaskApplication.objects.filter(
        task=task,
        doer=request.user
    ).first()
    
    if existing_app:
        if existing_app.status == 'pending':
            messages.info(request, f"You already applied for this task. Waiting for {task.poster.fullname} to review your application.")
        elif existing_app.status == 'accepted':
            messages.info(request, "You have been accepted for this task! You can now start working.")
        elif existing_app.status == 'rejected':
            messages.warning(request, "Your application was rejected. You can apply again if you'd like.")
        return redirect('task_detail', task_id=task_id)
    
    # ✅ NEW: Redirect to apply instead of direct accept
    messages.info(request, "Please submit an application for this task. The poster will review and choose the best applicant.")
    return redirect('apply_for_task', task_id=task_id)


@login_required
def complete_task(request, task_id):
    """Mark task as completed (Task Doers only)"""
    task = get_object_or_404(Task, id=task_id)
    
    if task.doer != request.user:
        messages.error(request, "You can only complete tasks assigned to you.")
        return redirect('task_detail', task_id=task_id)
    
    if task.status != 'in_progress':
        messages.error(request, "This task cannot be completed.")
        return redirect('task_detail', task_id=task_id)
    
    task.status = 'completed'
    task.completed_at = timezone.now()
    task.save()
    
    # Create notification for poster
    Notification.objects.create(
        user=task.poster,
        type='task_completed',
        title=f'Task "{task.title}" Completed',
        message=f'{request.user.fullname} has completed your task. Please review and rate the doer.',
        related_task=task
    )
    
    # IMPORTANT: Remind doer to rate poster too
    Notification.objects.create(
        user=request.user,
        type='system_message',
        title='Please Rate Your Experience',
        message=f'You completed "{task.title}". Please rate your experience with {task.poster.fullname}.',
        related_task=task
    )
    
    messages.success(request, f"Task '{task.title}' marked as completed! Don't forget to rate {task.poster.fullname}.")
    return redirect('task_detail', task_id=task_id)


@login_required
def my_tasks(request):
    """View user's tasks (posted or accepted)"""
    if request.user.role == 'task_poster':
        tasks = Task.objects.filter(poster=request.user).select_related('doer').order_by('-created_at')
    elif request.user.role == 'task_doer':
        tasks = Task.objects.filter(doer=request.user).select_related('poster').order_by('-accepted_at')
    else:
        # Admin sees all tasks
        tasks = Task.objects.all().select_related('poster', 'doer').order_by('-created_at')
    
    # ✅ OPTIMIZED: Calculate status counts using aggregation (single query)
    from django.db.models import Count, Q
    status_counts_query = tasks.aggregate(
        open=Count('id', filter=Q(status='open')),
        in_progress=Count('id', filter=Q(status='in_progress')),
        completed=Count('id', filter=Q(status='completed')),
        accepted=Count('id', filter=Q(status='accepted')),
    )
    status_counts = {
        'open': status_counts_query['open'],
        'in_progress': status_counts_query['in_progress'],
        'completed': status_counts_query['completed'],
        'accepted': status_counts_query['accepted'],
    }
    
    # Pagination
    paginator = Paginator(tasks, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'tasks/my_tasks_modern.html', {
        'tasks': page_obj,
        'status_counts': status_counts,
    })


@login_required
def send_message(request, task_id):
    """Send a message in task chat with 5-message limit enforcement"""
    task = get_object_or_404(Task, id=task_id)
    
    # Check if user can send messages
    if not (task.poster == request.user or task.doer == request.user):
        messages.error(request, "You can only message in tasks you're involved in.")
        return redirect('task_detail', task_id=task_id)
    
    # Check chat access (5-message limit)
    chat_access = check_chat_access(task_id, request.user)
    if not chat_access['allowed']:
        messages.error(request, chat_access['reason'])
        return redirect('task_detail', task_id=task_id)
    
    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.task = task
            message.sender = request.user
            
            # Compress image attachments before saving
            if 'attachment' in request.FILES:
                attachment = request.FILES['attachment']
                # Check if it's an image file
                if attachment.content_type.startswith('image/'):
                    compressed_attachment = compress_chat_image(attachment)
                    message.attachment = compressed_attachment
            
            message.save()
            
            # Create notification for the other party
            recipient = task.doer if task.poster == request.user else task.poster
            if recipient:
                Notification.objects.create(
                    user=recipient,
                    type='system_message',
                    title=f'New message in "{task.title}"',
                    message=f'{request.user.fullname} sent you a message.',
                    related_task=task
                )
            
            # Show warning if approaching limit
            if chat_access.get('free_tier') and chat_access.get('messages_remaining', 0) <= 2:
                remaining = chat_access['messages_remaining'] - 1  # Account for message just sent
                if remaining > 0:
                    messages.warning(request, f"⚠️ {remaining} free message(s) remaining. Pay ₱2 to unlock unlimited chat.")
                else:
                    messages.warning(request, "⚠️ This was your last free message. Pay ₱2 to continue chatting.")
            else:
                messages.success(request, "Message sent!")
    
    return redirect('task_detail', task_id=task_id)


# ==================== SKILL VALIDATION VIEWS ====================

@login_required
def skill_validation(request):
    """Skill validation page for Task Doers"""
    if request.user.role != 'task_doer':
        messages.error(request, "Only Task Doers can validate skills.")
        return redirect('dashboard')
    
    # Get user's skills
    user_skills = StudentSkill.objects.filter(student=request.user)
    
    if request.method == 'POST':
        form = SkillValidationForm(request.POST, request.FILES)
        if form.is_valid():
            # Check if skill already exists
            skill_name = form.cleaned_data['skill_name']
            if user_skills.filter(skill_name=skill_name).exists():
                messages.error(request, f"You have already submitted {skill_name} for validation.")
            else:
                skill = form.save(commit=False)
                skill.student = request.user
                
                # Compress proof file if it's an image
                if 'proof_url' in request.FILES:
                    proof_file = request.FILES['proof_url']
                    if proof_file.content_type.startswith('image/'):
                        compressed_proof = compress_image(proof_file)
                        skill.proof_url = compressed_proof
                
                skill.save()
                
                # Redirect to typing test if skill is typing
                if skill_name == 'typing':
                    messages.success(request, "Skill submitted! Please complete the typing test.")
                    return redirect('typing_test', skill_id=skill.id)
                else:
                    messages.success(request, f"{skill_name} skill submitted for validation!")
                    return redirect('skill_validation')
    else:
        form = SkillValidationForm()
    
    context = {
        'form': form,
        'user_skills': user_skills
    }
    
    return render(request, 'skills/skill_validation.html', context)


@login_required
def typing_test(request, skill_id):
    """Typing test with 50 multiple choice questions"""
    skill = get_object_or_404(StudentSkill, id=skill_id, student=request.user)
    
    # Check if already completed
    if skill.test_score is not None:
        messages.info(request, "You have already completed this test.")
        return redirect('skill_validation')
    
    if request.method == 'POST':
        # Get answers from form
        answers = {}
        for i in range(1, 51):  # 50 questions
            answer_key = f'question_{i}'
            if answer_key in request.POST:
                answers[i] = request.POST[answer_key]
        
        # Correct answers for 50 questions
        correct_answers = {
            # Basic Typing Knowledge (1-10)
            1: 'b', 2: 'c', 3: 'b', 4: 'a', 5: 'c', 6: 'b', 7: 'a', 8: 'c', 9: 'b', 10: 'a',
            # Keyboard Layout (11-20)
            11: 'a', 12: 'b', 13: 'c', 14: 'a', 15: 'b', 16: 'c', 17: 'a', 18: 'b', 19: 'c', 20: 'a',
            # Typing Techniques (21-30)
            21: 'b', 22: 'c', 23: 'a', 24: 'b', 25: 'c', 26: 'a', 27: 'b', 28: 'c', 29: 'a', 30: 'b',
            # Speed & Accuracy (31-40)
            31: 'c', 32: 'a', 33: 'b', 34: 'c', 35: 'a', 36: 'b', 37: 'c', 38: 'a', 39: 'b', 40: 'c',
            # Professional Typing (41-50)
            41: 'a', 42: 'b', 43: 'c', 44: 'a', 45: 'b', 46: 'c', 47: 'a', 48: 'b', 49: 'c', 50: 'a',
        }
        
        # Calculate score
        correct_count = sum(1 for q, ans in answers.items() if correct_answers.get(q) == ans)
        score = (correct_count / 50) * 100
        
        # Save score
        skill.test_score = int(score)
        skill.save()
        
        # Check if passed
        if score >= 75:
            messages.success(request, f"Congratulations! You scored {score:.0f}% ({correct_count}/50 correct). Your skill is now pending admin review.")
        else:
            messages.warning(request, f"You scored {score:.0f}% ({correct_count}/50 correct). You need 75% or higher. Please try again later.")
            skill.status = 'rejected'
            skill.notes = f"Test score: {score:.0f}% ({correct_count}/50) - Below minimum requirement of 75%"
            skill.save()
        
        return redirect('skill_validation')
    
    return render(request, 'skills/typing_test.html', {'skill': skill})


@login_required
def delete_skill(request, skill_id):
    """Delete a skill submission"""
    skill = get_object_or_404(StudentSkill, id=skill_id, student=request.user)
    
    # Only allow deletion if not verified
    if skill.status == 'verified':
        messages.error(request, "Cannot delete a verified skill.")
        return redirect('skill_validation')
    
    skill_name = skill.get_skill_name_display()
    skill.delete()
    messages.success(request, f"{skill_name} skill has been deleted.")
    return redirect('skill_validation')


# ==================== PAYMENT VIEWS ====================

@login_required
def gcash_payment_form(request, task_id):
    """🎯 GCash Pre-Payment Form - Collect user info before payment"""
    task = get_object_or_404(Task, id=task_id)
    
    # Only task poster can pay system fee
    if task.poster != request.user:
        messages.error(request, "Only the task poster can pay the system fee.")
        return redirect('task_detail', task_id=task_id)
    
    # Check if already paid
    if hasattr(task, 'commission') and task.commission.status == 'paid':
        messages.info(request, "System fee has already been paid for this task.")
        return redirect('task_detail', task_id=task_id)
    
    if request.method == 'POST':
        # Collect GCash payment info
        fullname = request.POST.get('fullname', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        gcash_number = request.POST.get('gcash_number', '').strip()
        
        # Validate required fields
        if not all([fullname, phone, email]):
            messages.error(request, "Please fill in all required fields.")
            return render(request, 'payments/gcash_form.html', {
                'task': task,
                'fullname': fullname,
                'phone': phone,
                'email': email,
                'gcash_number': gcash_number
            })
        
        # Store payment info in session
        request.session['gcash_fullname'] = fullname
        request.session['gcash_phone'] = phone
        request.session['gcash_email'] = email
        request.session['gcash_number'] = gcash_number
        request.session['payment_task_id'] = str(task.id)
        request.session['payment_type'] = 'system_fee'
        
        logger.info(f"GCash payment form submitted for task {task_id}")
        logger.info(f"User: {fullname} | Phone: {phone} | Email: {email}")
        
        # Redirect to actual payment processing
        return redirect('gcash_payment_process', task_id=task_id)
    
    # Pre-fill with user data
    context = {
        'task': task,
        'fullname': request.user.fullname or '',
        'email': request.user.email or '',
        'phone': request.user.phone_number or ''
    }
    return render(request, 'payments/gcash_form.html', context)


@login_required
def gcash_payment_process(request, task_id):
    """🔄 Process GCash Payment - Redirect to PayMongo after form submission"""
    task = get_object_or_404(Task, id=task_id)
    
    # Verify user has submitted the form
    if 'gcash_fullname' not in request.session:
        messages.error(request, "Please fill in payment information first.")
        return redirect('gcash_payment_form', task_id=task_id)
    
    from .paymongo import ErrandExpressPayments
    payments = ErrandExpressPayments()
    
    # Get GCash info from session
    gcash_info = {
        'fullname': request.session.get('gcash_fullname'),
        'phone': request.session.get('gcash_phone'),
        'email': request.session.get('gcash_email'),
        'gcash_number': request.session.get('gcash_number', '')
    }
    
    # Create payment with GCash info in description
    description = f"ErrandExpress System Fee - {task.title} | {gcash_info['fullname']} | {gcash_info['phone']}"
    
    result = payments.process_gcash_payment(
        amount=payments.system_fee,
        description=description,
        success_url=request.build_absolute_uri(reverse('payment_success')),
        failed_url=request.build_absolute_uri(reverse('payment_failed'))
    )
    
    if result['success']:
        # Store payment info in session
        request.session['payment_source_id'] = result['source_id']
        request.session['payment_task_id'] = str(task.id)
        request.session['payment_type'] = 'system_fee'
        
        logger.info(f"✅ GCash payment initiated for task {task_id}")
        logger.info(f"Payer: {gcash_info['fullname']} | Phone: {gcash_info['phone']}")
        
        return redirect(result['checkout_url'])
    else:
        messages.error(request, f"Payment failed: {result['error']}")
        return redirect('gcash_payment_form', task_id=task_id)


@login_required
def payment_system_fee(request, task_id):
    """Handle ₱2 system fee payment"""
    task = get_object_or_404(Task, id=task_id)
    
    # Only task poster can pay system fee
    if task.poster != request.user:
        messages.error(request, "Only the task poster can pay the system fee.")
        return redirect('task_detail', task_id=task_id)
    
    # Check if already paid
    if hasattr(task, 'commission') and task.commission.status == 'paid':
        messages.info(request, "System fee has already been paid for this task.")
        return redirect('task_detail', task_id=task_id)
    
    from .paymongo import ErrandExpressPayments
    payments = ErrandExpressPayments()
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method', 'gcash')
        
        if payment_method == 'gcash':
            # Redirect to GCash form instead of direct payment
            return redirect('gcash_payment_form', task_id=task_id)
        
        elif payment_method == 'card':
            result = payments.create_system_fee_payment(task, request.user)
            
            if result['success']:
                context = {
                    'task': task,
                    'payment_intent': result['payment_intent'],
                    'commission': result['commission'],
                    'public_key': settings.PAYMONGO_PUBLIC_KEY
                }
                return render(request, 'payments/card_payment.html', context)
            else:
                messages.error(request, f"Payment setup failed: {result['error']}")
    
    context = {
        'task': task,
        'system_fee': payments.system_fee,
        'payment_methods': [
            {'value': 'gcash', 'name': 'GCash', 'icon': '💳'},
            {'value': 'card', 'name': 'Credit/Debit Card', 'icon': '💳'},
        ]
    }
    
    return render(request, 'payments/system_fee.html', context)


@login_required
def payment_task_doer(request, task_id):
    """Handle task doer payment (for online payment method) - Pre-payment form"""
    task = get_object_or_404(Task, id=task_id)
    
    # Only task poster can pay task doer
    if task.poster != request.user:
        messages.error(request, "Only the task poster can pay the task doer.")
        return redirect('task_detail', task_id=task_id)
    
    # Only for online payment method
    if task.payment_method != 'online':
        messages.error(request, "Task doer payment is only for online payment method.")
        return redirect('task_detail', task_id=task_id)
    
    # Check if already paid
    payment = Payment.objects.filter(
        task=task,
        payer=request.user,
        receiver=task.doer,
        status='confirmed'
    ).first()
    
    if payment:
        messages.info(request, "Task doer has already been paid for this task.")
        return redirect('task_detail', task_id=task_id)
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method', 'gcash')
        
        if payment_method == 'gcash':
            # Collect GCash payment info before redirecting to PayMongo
            fullname = request.POST.get('fullname', '').strip()
            phone = request.POST.get('phone', '').strip()
            email = request.POST.get('email', '').strip()
            gcash_number = request.POST.get('gcash_number', '').strip()
            
            # Validate required fields
            if not all([fullname, phone, email]):
                messages.error(request, "Please fill in all required fields.")
                return render(request, 'payments/task_doer_payment.html', {
                    'task': task,
                    'amount': task.price,
                    'doer': task.doer,
                    'fullname': fullname,
                    'phone': phone,
                    'email': email,
                    'gcash_number': gcash_number,
                    'payment_methods': [
                        {'value': 'gcash', 'name': 'GCash', 'icon': '💳'},
                        {'value': 'card', 'name': 'Credit/Debit Card', 'icon': '💳'},
                    ]
                })
            
            # Store payment info in session
            request.session['gcash_fullname'] = fullname
            request.session['gcash_phone'] = phone
            request.session['gcash_email'] = email
            request.session['gcash_number'] = gcash_number
            request.session['payment_task_id'] = str(task.id)
            request.session['payment_type'] = 'task_payment'
            
            logger.info(f"Task doer payment form submitted for task {task_id}")
            logger.info(f"User: {fullname} | Phone: {phone} | Email: {email}")
            
            # Redirect to payment processing
            return redirect('payment_task_doer_process', task_id=task_id)
        
        elif payment_method == 'card':
            # For card, also collect info
            fullname = request.POST.get('fullname', '').strip()
            phone = request.POST.get('phone', '').strip()
            email = request.POST.get('email', '').strip()
            
            # Validate required fields
            if not all([fullname, phone, email]):
                messages.error(request, "Please fill in all required fields.")
                return render(request, 'payments/task_doer_payment.html', {
                    'task': task,
                    'amount': task.price,
                    'doer': task.doer,
                    'fullname': fullname,
                    'phone': phone,
                    'email': email,
                    'payment_methods': [
                        {'value': 'gcash', 'name': 'GCash', 'icon': '💳'},
                        {'value': 'card', 'name': 'Credit/Debit Card', 'icon': '💳'},
                    ]
                })
            
            # Store payment info in session
            request.session['card_fullname'] = fullname
            request.session['card_phone'] = phone
            request.session['card_email'] = email
            request.session['payment_task_id'] = str(task.id)
            request.session['payment_type'] = 'task_payment'
            
            logger.info(f"Task doer card payment form submitted for task {task_id}")
            
            # Redirect to card payment processing
            return redirect('payment_task_doer_card', task_id=task_id)
    
    context = {
        'task': task,
        'amount': task.price,
        'doer': task.doer,
        'fullname': request.user.fullname or '',
        'email': request.user.email or '',
        'phone': request.user.phone_number or '',
        'payment_methods': [
            {'value': 'gcash', 'name': 'GCash', 'icon': '💳'},
            {'value': 'card', 'name': 'Credit/Debit Card', 'icon': '💳'},
        ]
    }
    
    return render(request, 'payments/task_doer_payment.html', context)


@login_required
def payment_task_doer_process(request, task_id):
    """Process task doer GCash payment - Redirect to PayMongo"""
    task = get_object_or_404(Task, id=task_id)
    
    # Verify user has submitted the form
    if 'gcash_fullname' not in request.session:
        messages.error(request, "Please fill in payment information first.")
        return redirect('payment_task_doer', task_id=task_id)
    
    from .paymongo import ErrandExpressPayments
    payments = ErrandExpressPayments()
    
    # Get GCash info from session
    gcash_info = {
        'fullname': request.session.get('gcash_fullname'),
        'phone': request.session.get('gcash_phone'),
        'email': request.session.get('gcash_email'),
        'gcash_number': request.session.get('gcash_number', '')
    }
    
    # Create payment with GCash info in description
    description = f"ErrandExpress Task Payment - {task.title} | {gcash_info['fullname']} | {gcash_info['phone']}"
    
    result = payments.process_gcash_payment(
        amount=float(task.price),
        description=description,
        success_url=request.build_absolute_uri(reverse('payment_success')),
        failed_url=request.build_absolute_uri(reverse('payment_failed'))
    )
    
    if result['success']:
        # Store payment info in session
        request.session['payment_source_id'] = result['source_id']
        request.session['payment_task_id'] = str(task.id)
        request.session['payment_type'] = 'task_payment'
        
        logger.info(f"✅ Task doer GCash payment initiated for task {task_id}")
        logger.info(f"Amount: ₱{task.price} | Payer: {gcash_info['fullname']}")
        
        return redirect(result['checkout_url'])
    else:
        messages.error(request, f"Payment failed: {result['error']}")
        return redirect('payment_task_doer', task_id=task_id)


@login_required
def payment_task_doer_card(request, task_id):
    """Process task doer card payment"""
    task = get_object_or_404(Task, id=task_id)
    
    # Verify user has submitted the form
    if 'card_fullname' not in request.session:
        messages.error(request, "Please fill in payment information first.")
        return redirect('payment_task_doer', task_id=task_id)
    
    from .paymongo import ErrandExpressPayments
    payments = ErrandExpressPayments()
    
    # Get card info from session
    card_info = {
        'fullname': request.session.get('card_fullname'),
        'phone': request.session.get('card_phone'),
        'email': request.session.get('card_email')
    }
    
    # Create payment intent
    description = f"ErrandExpress Task Payment - {task.title} | {card_info['fullname']}"
    
    result = payments.process_card_payment(
        amount=float(task.price),
        description=description,
        success_url=request.build_absolute_uri(reverse('payment_success')),
        failed_url=request.build_absolute_uri(reverse('payment_failed'))
    )
    
    if result['success']:
        # Store payment info in session
        request.session['payment_source_id'] = result['source_id']
        request.session['payment_task_id'] = str(task.id)
        request.session['payment_type'] = 'task_payment'
        
        logger.info(f"✅ Task doer card payment initiated for task {task_id}")
        logger.info(f"Amount: ₱{task.price} | Payer: {card_info['fullname']}")
        
        return redirect(result['checkout_url'])
    else:
        messages.error(request, f"Payment failed: {result['error']}")
        return redirect('payment_task_doer', task_id=task_id)


@login_required
def payment_success(request):
    """Handle successful payment callback"""
    # Get payment info from session
    source_id = request.session.get('payment_source_id')
    task_id = request.session.get('payment_task_id')
    payment_type = request.session.get('payment_type')
    
    if not all([source_id, task_id, payment_type]):
        messages.error(request, "Invalid payment session.")
        return redirect('dashboard')
    
    task = get_object_or_404(Task, id=task_id)
    
    if payment_type == 'system_fee':
        # Update system commission status
        try:
            from .models import SystemCommission, SystemWallet
            logger.info(f"Processing system fee payment for task {task_id}")
            
            # Check if commission exists
            if not hasattr(task, 'commission'):
                logger.warning(f"⚠️ SystemCommission not found for task {task_id} - creating one now")
                
                # Auto-create missing commission (fallback)
                commission = SystemCommission.objects.create(
                    task=task,
                    payer=task.poster,
                    amount=2.00,
                    method='online',
                    status='paid',
                    paid_at=timezone.now()
                )
                logger.info(f"✅ Auto-created commission: {commission.id}")
            else:
                commission = task.commission
                logger.info(f"Found commission: {commission.id}, current status: {commission.status}")
                
                commission.status = 'paid'
                commission.paid_at = timezone.now()
                commission.save()
                logger.info(f"✅ Commission status updated to 'paid'")
            
            # 💰 ADD REVENUE TO SYSTEM WALLET
            wallet = SystemWallet.get_or_create_wallet()
            wallet.add_revenue(
                amount=commission.amount,
                description=f"System fee from task: {task.title}"
            )
            logger.info(f"💰 Revenue added to wallet: ₱{commission.amount}")
            
            # 🔔 UNLOCK CHAT IMMEDIATELY
            task.chat_unlocked = True
            task.save()
            logger.info(f"✅ Chat unlocked for task {task_id}")
            
            # Notify poster
            Notification.objects.create(
                user=task.poster,
                type='payment_confirmed',
                title='₱2 System Fee Paid! 💳',
                message=f'System fee paid successfully. Chat unlocked for "{task.title}"',
                related_task=task
            )
            logger.info(f"✅ Notification created for user {task.poster.id}")
            
            logger.info(f"✅ System fee payment confirmed - chat unlocked for task {task_id}")
            messages.success(request, "✅ Payment successful! Chat unlocked. Opening chat now...")
            
            # 💬 REDIRECT TO CHAT INSTEAD OF TASK DETAIL
            # Clear session first
            for key in ['payment_source_id', 'payment_task_id', 'payment_type', 'gcash_fullname', 'gcash_phone', 'gcash_email', 'gcash_number']:
                request.session.pop(key, None)
            
            # Redirect to chat page
            return redirect('chat', task_id=task_id)
            
        except Exception as e:
            logger.error(f"❌ Payment verification error: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            messages.error(request, f"Payment verification failed: {str(e)}")
            
            # Clear session on error
            for key in ['payment_source_id', 'payment_task_id', 'payment_type', 'gcash_fullname', 'gcash_phone', 'gcash_email', 'gcash_number']:
                request.session.pop(key, None)
            
            return redirect('task_detail', task_id=task_id)
    
    elif payment_type == 'task_payment':
        # Handle task doer payment
        try:
            from .models import Payment, SystemWallet
            logger.info(f"Processing task doer payment for task {task_id}")
            
            # Create Payment record for task doer
            payment = Payment.objects.create(
                task=task,
                payer=task.poster,
                receiver=task.doer,
                amount=task.price,
                method='online',
                status='confirmed',
                paymongo_payment_id=source_id,
                confirmed_at=timezone.now()
            )
            logger.info(f"✅ Payment record created: {payment.id}")
            
            # 💰 ADD REVENUE TO SYSTEM WALLET (10% commission)
            wallet = SystemWallet.get_or_create_wallet()
            commission_amount = float(task.price) * 0.10
            wallet.add_revenue(
                amount=commission_amount,
                description=f"Commission from task payment: {task.title}"
            )
            logger.info(f"💰 Commission added to wallet: ₱{commission_amount}")
            
            # Notify task doer about payment
            Notification.objects.create(
                user=task.doer,
                type='payment_received',
                title='Payment Received! 💰',
                message=f'You received ₱{task.price} for completing "{task.title}"',
                related_task=task
            )
            logger.info(f"✅ Notification created for task doer {task.doer.id}")
            
            # Notify task poster
            Notification.objects.create(
                user=task.poster,
                type='payment_confirmed',
                title='Task Doer Payment Confirmed! 💳',
                message=f'Payment of ₱{task.price} sent to task doer for "{task.title}". You can now rate them.',
                related_task=task
            )
            logger.info(f"✅ Notification created for task poster {task.poster.id}")
            
            logger.info(f"✅ Task doer payment confirmed for task {task_id}")
            messages.success(request, f"✅ Payment successful! ₱{task.price} sent to {task.doer.fullname}. You can now rate them.")
            
            # Clear session
            for key in ['payment_source_id', 'payment_task_id', 'payment_type', 'gcash_fullname', 'gcash_phone', 'gcash_email', 'gcash_number']:
                request.session.pop(key, None)
            
            # Redirect to rating page
            return redirect('rate_user', task_id=task_id, user_id=task.doer.id)
            
        except Exception as e:
            logger.error(f"❌ Task payment processing error: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            messages.error(request, f"Payment processing failed: {str(e)}")
            
            # Clear session on error
            for key in ['payment_source_id', 'payment_task_id', 'payment_type', 'gcash_fullname', 'gcash_phone', 'gcash_email', 'gcash_number']:
                request.session.pop(key, None)
            
            return redirect('task_detail', task_id=task_id)


@login_required
def payment_failed(request):
    """Handle failed payment callback"""
    messages.error(request, "Payment was cancelled or failed. Please try again.")
    
    # Get task ID from session and redirect
    task_id = request.session.get('payment_task_id')
    if task_id:
        return redirect('task_detail', task_id=task_id)
    
    return redirect('dashboard')


@login_required
def test_manual_payment_confirm(request, task_id):
    """🧪 TEST ENDPOINT: Manually confirm payment for debugging"""
    task = get_object_or_404(Task, id=task_id)
    
    # Only task poster can confirm
    if task.poster != request.user:
        messages.error(request, "Only task poster can confirm payment.")
        return redirect('task_detail', task_id=task_id)
    
    try:
        from .models import SystemCommission
        logger.info(f"🧪 TEST: Manually confirming payment for task {task_id}")
        
        # Check if commission exists
        if not hasattr(task, 'commission'):
            logger.warning(f"⚠️ Creating missing commission for task {task_id}")
            commission = SystemCommission.objects.create(
                task=task,
                payer=task.poster,
                amount=2.00,
                method='online',
                status='paid',
                paid_at=timezone.now()
            )
        else:
            commission = task.commission
            commission.status = 'paid'
            commission.paid_at = timezone.now()
            commission.save()
        
        # Unlock chat
        task.chat_unlocked = True
        task.save()
        
        # Notify
        Notification.objects.create(
            user=task.poster,
            type='payment_confirmed',
            title='₱2 System Fee Paid! 💳',
            message=f'System fee paid successfully. Chat unlocked for "{task.title}"',
            related_task=task
        )
        
        logger.info(f"✅ TEST: Payment confirmed - chat unlocked for task {task_id}")
        messages.success(request, "✅ TEST: Payment confirmed! Chat unlocked.")
        
    except Exception as e:
        logger.error(f"❌ TEST: Error confirming payment: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        messages.error(request, f"Error: {str(e)}")
    
    return redirect('task_detail', task_id=task_id)


# ==================== RATING AND REVIEW VIEWS ====================

@login_required
def task_monitoring(request):
    """Task monitoring dashboard for faculty and students"""
    user = request.user
    
    if user.role == 'task_poster':
        # Faculty view: Monitor posted tasks
        tasks = Task.objects.filter(poster=user).select_related('doer').order_by('-created_at')
        
        # Calculate statistics
        total_tasks = tasks.count()
        completed_tasks = tasks.filter(status='completed').count()
        in_progress = tasks.filter(status='in_progress').count()
        pending = tasks.filter(status='open').count()
        
        context = {
            'tasks': tasks,
            'stats': {
                'total': total_tasks,
                'completed': completed_tasks,
                'in_progress': in_progress,
                'pending': pending,
                'completion_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            },
            'role': 'poster'
        }
        
    elif user.role == 'task_doer':
        # Student view: Monitor assigned tasks
        tasks = Task.objects.filter(doer=user).select_related('poster').order_by('-created_at')
        
        # Calculate statistics
        total_tasks = tasks.count()
        completed_tasks = tasks.filter(status='completed').count()
        in_progress = tasks.filter(status='in_progress').count()
        pending = tasks.filter(status='open').count()
        
        context = {
            'tasks': tasks,
            'stats': {
                'total': total_tasks,
                'completed': completed_tasks,
                'in_progress': in_progress,
                'pending': pending,
                'completion_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            },
            'role': 'doer'
        }
    else:
        return redirect('dashboard')
    
    return render(request, 'monitoring/task_monitoring.html', context)


@login_required
def rate_user(request, task_id, user_id):
    """Rate a user after task completion with payment enforcement"""
    task = get_object_or_404(Task, id=task_id)
    rated_user = get_object_or_404(User, id=user_id)
    
    # Enhanced verification checks
    if task.status != 'completed':
        messages.error(request, "You can only rate users after task completion.")
        return redirect('task_detail', task_id=task_id)
    
    # Check if user is part of this task
    if request.user not in [task.poster, task.doer]:
        messages.error(request, "You are not part of this task.")
        return redirect('task_detail', task_id=task_id)
    
    # Check if trying to rate themselves
    if rated_user == request.user:
        messages.error(request, "You cannot rate yourself.")
        return redirect('task_detail', task_id=task_id)
    
    # Check if rated_user is part of this task
    if rated_user not in [task.poster, task.doer]:
        messages.error(request, "This user is not part of this task.")
        return redirect('task_detail', task_id=task_id)
    
    # ✅ NEW: PAYMENT ENFORCEMENT FOR RATING
    # Task poster must pay before rating task doer
    if request.user == task.poster and rated_user == task.doer:
        # Check if chat is unlocked (system commission paid)
        if not task.chat_unlocked:
            messages.error(request, "You must pay the ₱2 system fee to unlock chat before rating.")
            return redirect('payment_system_fee', task_id=task_id)
        
        # For online payment: must also pay the task doer
        if task.payment_method == 'online':
            payment = Payment.objects.filter(
                task=task,
                payer=request.user,
                receiver=task.doer,
                status='confirmed'
            ).first()
            
            if not payment:
                messages.error(request, "You must pay the task doer before rating them. Please complete the payment first.")
                return redirect('payment_task_doer', task_id=task_id)
    
    # Check if already rated
    existing_rating = Rating.objects.filter(
        task=task,
        rater=request.user,
        rated=rated_user
    ).first()
    
    if request.method == 'POST':
        # Prevent duplicate ratings
        if existing_rating:
            messages.warning(request, "You have already rated this user for this task. You cannot rate them again.")
            return redirect('task_detail', task_id=task_id)
        
        form = RatingForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.task = task
            rating.rater = request.user
            rating.rated = rated_user
            rating.save()
            
            # IMPROVED: Recalculate average rating from all ratings (more accurate)
            all_ratings = Rating.objects.filter(rated=rated_user)
            if all_ratings.exists():
                avg_rating = all_ratings.aggregate(Avg('score'))['score__avg']
                rated_user.avg_rating = round(avg_rating, 2)
                rated_user.total_ratings = all_ratings.count()
                rated_user.save()
                logger.info(f"Updated {rated_user.fullname}'s rating: {rated_user.avg_rating} ({rated_user.total_ratings} ratings)")
            
            # Create notification
            Notification.objects.create(
                user=rated_user,
                type='rating_received',
                title='New Rating Received',
                message=f'{request.user.fullname} rated you {rating.score}/10 for "{task.title}"',
                related_task=task
            )
            
            messages.success(request, f"Rating submitted successfully! {rated_user.fullname} now has {rated_user.total_ratings} rating(s).")
            return redirect('task_detail', task_id=task_id)
    else:
        form = RatingForm()
    
    context = {
        'form': form,
        'task': task,
        'rated_user': rated_user,
        'already_rated': bool(existing_rating),
        'existing_rating': existing_rating
    }
    
    return render(request, 'ratings/rate_user.html', context)


# ==================== TASK APPLICATION SYSTEM ====================

@login_required
def apply_for_task(request, task_id):
    """
    Doer applies for a task - solves the multiple applicants problem
    """
    task = get_object_or_404(Task, id=task_id)
    
    # Verification checks
    if request.user.role != 'task_doer':
        messages.error(request, "Only task doers can apply for tasks.")
        return redirect('task_detail', task_id=task_id)
    
    if task.status != 'open':
        messages.error(request, "This task is no longer accepting applications.")
        return redirect('task_detail', task_id=task_id)
    
    if task.poster == request.user:
        messages.error(request, "You cannot apply to your own task.")
        return redirect('task_detail', task_id=task_id)
    
    # Check if already applied
    existing_app = TaskApplication.objects.filter(task=task, doer=request.user).first()
    if existing_app:
        if existing_app.status == 'pending':
            messages.info(request, "You have already applied to this task. Your application is pending review.")
        elif existing_app.status == 'accepted':
            messages.info(request, "Your application was accepted! You can now work on this task.")
        elif existing_app.status == 'rejected':
            messages.info(request, "Your previous application was not accepted.")
        return redirect('task_detail', task_id=task_id)
    
    if request.method == 'POST':
        form = TaskApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.task = task
            application.doer = request.user
            
            # Set first_application_time if this is the first application
            if not task.applications.exists():
                application.first_application_time = timezone.now()
                logger.info(f"⏱️ First application for task {task_id} - 3-minute window started")
            
            application.save()
            
            # Notify poster
            Notification.objects.create(
                user=task.poster,
                type='system_message',
                title='New Task Application',
                message=f'{request.user.fullname} applied for "{task.title}". Review applications to choose the best doer.',
                related_task=task
            )
            
            messages.success(request, "Application submitted successfully! The task poster will review your application.")
            return redirect('task_detail', task_id=task_id)
    else:
        form = TaskApplicationForm()
    
    # Get user stats for display
    completed_tasks = Task.objects.filter(doer=request.user, status='completed').count()
    user_ratings = Rating.objects.filter(rated=request.user)
    avg_rating = user_ratings.aggregate(Avg('score'))['score__avg'] or 0
    
    context = {
        'form': form,
        'task': task,
        'user_stats': {
            'rating': round(avg_rating, 1),
            'completed_tasks': completed_tasks,
            'is_newbie': completed_tasks < 3,
            'total_ratings': user_ratings.count(),
        }
    }
    
    return render(request, 'tasks/apply.html', context)


@login_required
def view_applications(request, task_id):
    """
    Poster views applications for their task with smart ranking
    Applications are ranked by: Rating + Experience + Newbie Bonus
    Shows doer ratings and validated skills
    """
    task = get_object_or_404(Task, id=task_id)
    
    # Verify poster owns this task
    if task.poster != request.user and request.user.role != 'admin':
        messages.error(request, "You can only view applications for your own tasks.")
        return redirect('task_detail', task_id=task_id)
    
    # ✅ OPTIMIZED: Get applications with prefetch_related to avoid N+1 queries
    from django.db.models import Count, Prefetch
    
    # Prefetch ratings and skills for each doer
    # ✅ NOTE: Don't use slice [:3] in Prefetch queryset - it prevents further filtering
    applications = TaskApplication.objects.filter(
        task=task
    ).select_related('doer').prefetch_related(
        Prefetch(
            'doer__received_ratings',
            queryset=Rating.objects.order_by('-created_at')
        ),
        Prefetch(
            'doer__skills',
            queryset=StudentSkill.objects.filter(status='verified')
        )
    ).order_by('-created_at')
    
    # Calculate real-time ratings and add to each application
    doer_rating_subquery = Rating.objects.filter(
        rated=OuterRef('doer')
    ).values('rated').annotate(
        avg_rating=Avg('score')
    ).values('avg_rating')
    
    applications = applications.annotate(
        doer_current_rating=Coalesce(
            Subquery(doer_rating_subquery, output_field=DecimalField(max_digits=3, decimal_places=2)),
            Value(0.0, output_field=DecimalField(max_digits=3, decimal_places=2)),
            output_field=DecimalField(max_digits=3, decimal_places=2)
        ),
        doer_completed_count=Count(
            'doer__assigned_tasks',
            filter=Q(doer__assigned_tasks__status='completed')
        )
    )
    
    # Calculate ranking score for each application
    app_list = list(applications)
    for app in app_list:
        # Update snapshot with current data
        app.current_rating = app.doer_current_rating
        app.current_completed = app.doer_completed_count
        app.current_is_newbie = app.doer_completed_count < 3
        
        # Calculate ranking score
        app.calculated_ranking_score = (
            (float(app.current_rating) * 10) + 
            (app.current_completed * 2) + 
            (15 if app.current_is_newbie else 0)
        )
        
        # ✅ OPTIMIZED: Use prefetched ratings
        app.recent_ratings = app.doer.received_ratings.all()[:3]
        
        # ✅ OPTIMIZED: Use prefetched skills
        app.validated_skills = [skill.skill_name for skill in app.doer.skills.all()]
        
        # Get skill display names
        skill_display_map = {
            'typing': '⌨️ Typing',
            'powerpoint': '📊 PowerPoint',
            'graphics': '🎨 Graphics Design'
        }
        app.validated_skills_display = [
            skill_display_map.get(skill, skill) 
            for skill in app.validated_skills
        ]
    
    # Sort by ranking score (highest first)
    app_list.sort(key=lambda x: x.calculated_ranking_score, reverse=True)
    
    # Separate by status
    pending_apps = [app for app in app_list if app.status == 'pending']
    accepted_apps = [app for app in app_list if app.status == 'accepted']
    rejected_apps = [app for app in app_list if app.status == 'rejected']
    
    context = {
        'task': task,
        'pending_applications': pending_apps,
        'accepted_applications': accepted_apps,
        'rejected_applications': rejected_apps,
        'pending_count': len(pending_apps),
        'total_count': len(app_list),
    }
    
    return render(request, 'tasks/applications.html', context)


@login_required
def accept_application(request, application_id):
    """Poster accepts an application"""
    application = get_object_or_404(TaskApplication, id=application_id)
    task = application.task
    
    # Verify poster owns this task
    if task.poster != request.user and request.user.role != 'admin':
        messages.error(request, "You can only accept applications for your own tasks.")
        return redirect('task_detail', task_id=task.id)
    
    if task.status != 'open':
        messages.error(request, "This task is no longer accepting applications.")
        return redirect('view_applications', task_id=task.id)
    
    # Accept the application
    application.status = 'accepted'
    application.reviewed_at = timezone.now()
    application.save()
    
    # Assign doer to task and change status to in_progress
    task.doer = application.doer
    task.status = 'in_progress'  # ✅ FIXED: Use 'in_progress' instead of 'accepted'
    task.accepted_at = timezone.now()
    task.save()
    
    # Reject all other pending applications
    TaskApplication.objects.filter(
        task=task,
        status='pending'
    ).exclude(id=application.id).update(
        status='rejected',
        reviewed_at=timezone.now()
    )
    
    # Notify accepted doer
    Notification.objects.create(
        user=application.doer,
        type='task_assigned',
        title='You were chosen for a task!',
        message=f'Your application for "{task.title}" was selected! You can now start working on it.',
        related_task=task
    )
    
    # Notify rejected doers
    rejected_doers = TaskApplication.objects.filter(
        task=task,
        status='rejected'
    ).exclude(id=application.id).values_list('doer', flat=True)
    
    for doer_id in rejected_doers:
        Notification.objects.create(
            user_id=doer_id,
            type='system_message',
            title='Application Not Selected',
            message=f'Thank you for applying to "{task.title}". The poster has chosen another applicant for this task.',
            related_task=task
        )
    
    messages.success(request, f"Selected {application.doer.fullname} for this task!")
    return redirect('task_detail', task_id=task.id)


@login_required
def reject_application(request, application_id):
    """Poster rejects an application"""
    application = get_object_or_404(TaskApplication, id=application_id)
    task = application.task
    
    # Verify poster owns this task
    if task.poster != request.user and request.user.role != 'admin':
        messages.error(request, "You can only reject applications for your own tasks.")
        return redirect('task_detail', task_id=task.id)
    
    # Reject the application
    application.status = 'rejected'
    application.reviewed_at = timezone.now()
    application.save()
    
    # Notify doer
    Notification.objects.create(
        user=application.doer,
        type='system_message',
        title='Application Not Selected',
        message=f'Your application for "{task.title}" was not selected. Keep applying to other tasks!',
        related_task=task
    )
    
    messages.success(request, "Application rejected.")
    return redirect('view_applications', task_id=task.id)


@login_required
def report_user(request, user_id):
    """Report a user"""
    reported_user = get_object_or_404(User, id=user_id)
    
    if reported_user == request.user:
        messages.error(request, "You cannot report yourself.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.reported = reported_user
            
            # Get task from form if provided
            task_id = request.POST.get('task_id')
            if task_id:
                try:
                    task = Task.objects.get(id=task_id)
                    report.task = task
                except Task.DoesNotExist:
                    pass
            
            report.save()
            
            # Create notification for admins
            admin_users = User.objects.filter(role='admin')
            for admin in admin_users:
                Notification.objects.create(
                    user=admin,
                    type='report_filed',
                    title='New User Report',
                    message=f'{request.user.fullname} reported {reported_user.fullname} for {report.get_reason_display()}',
                )
            
            messages.success(request, "Report submitted successfully. Our team will review it.")
            return redirect('dashboard')
    else:
        form = ReportForm()
    
    context = {
        'form': form,
        'reported_user': reported_user
    }
    
    return render(request, 'reports/report_user.html', context)


# ==================== NOTIFICATION VIEWS ====================

@login_required
def notifications(request):
    """View user notifications"""
    user_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # Mark notifications as read when viewed
    unread_notifications = user_notifications.filter(is_read=False)
    unread_notifications.update(is_read=True)
    
    # Pagination
    paginator = Paginator(user_notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'notifications': page_obj,
        'unread_count': unread_notifications.count()
    }
    
    return render(request, 'notifications/list.html', context)


@login_required
def notification_count(request):
    """Get unread notification count (AJAX)"""
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'count': count})


@login_required
def api_notifications_recent(request):
    """Get recent notifications for dropdown (AJAX)"""
    from django.utils.timesince import timesince
    
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:10]
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    
    notifications_data = []
    for notif in notifications:
        notifications_data.append({
            'id': str(notif.id),
            'type': notif.type,
            'title': notif.title,
            'message': notif.message,
            'is_read': notif.is_read,
            'time_ago': timesince(notif.created_at) + ' ago',
            'created_at': notif.created_at.isoformat()
        })
    
    return JsonResponse({
        'notifications': notifications_data,
        'unread_count': unread_count
    })


@login_required
def api_notifications_count(request):
    """Get unread notification count for badge (AJAX)"""
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'unread_count': unread_count})


@login_required
def api_notifications_mark_as_read(request):
    """Mark all unread notifications as read (AJAX)"""
    if request.method == 'POST':
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return JsonResponse({'status': 'success', 'message': 'All notifications marked as read'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


@login_required
def api_tasks_updates(request):
    """Get new tasks count for task doers (AJAX polling)"""
    try:
        # Get the last check time from query params (if provided)
        last_check = request.GET.get('last_check')
        
        # Get new open tasks for this user
        if request.user.role == 'task_doer':
            from core.algorithms import get_matched_tasks_for_user
            new_tasks = get_matched_tasks_for_user(request.user)
            new_tasks_count = new_tasks.count() if new_tasks else 0
        else:
            new_tasks_count = 0
        
        return JsonResponse({
            'new_tasks': new_tasks_count,
            'status': 'success'
        })
    except Exception as e:
        logger.error(f"Error in api_tasks_updates: {str(e)}")
        return JsonResponse({
            'new_tasks': 0,
            'status': 'error',
            'message': str(e)
        }, status=500)


# ==================== ADMIN DASHBOARD VIEWS ====================

@login_required
def admin_dashboard(request):
    """Admin dashboard with system overview"""
    if request.user.role != 'admin':
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('dashboard')
    
    from django.db.models import Count, Sum, Avg
    from datetime import datetime, timedelta
    
    # Get date ranges
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # User statistics
    total_users = User.objects.count()
    new_users_week = User.objects.filter(date_joined__gte=week_ago).count()
    task_posters = User.objects.filter(role='task_poster').count()
    task_doers = User.objects.filter(role='task_doer').count()
    
    # Task statistics
    total_tasks = Task.objects.count()
    open_tasks = Task.objects.filter(status='open').count()
    in_progress_tasks = Task.objects.filter(status='in_progress').count()
    completed_tasks = Task.objects.filter(status='completed').count()
    tasks_this_week = Task.objects.filter(created_at__gte=week_ago).count()
    
    # Financial statistics
    total_revenue = SystemCommission.objects.filter(status='paid').aggregate(
        total=Sum('amount'))['total'] or 0
    revenue_this_month = SystemCommission.objects.filter(
        status='paid', 
        paid_at__gte=month_ago
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Skill validation statistics
    pending_skills = StudentSkill.objects.filter(status='pending').count()
    verified_skills = StudentSkill.objects.filter(status='verified').count()
    
    # Recent activity
    recent_tasks = Task.objects.select_related('poster', 'doer').order_by('-created_at')[:10]
    recent_users = User.objects.order_by('-date_joined')[:10]
    pending_reports = Report.objects.filter(status='pending').count()
    
    # Category breakdown
    category_stats = Task.objects.values('category').annotate(
        count=Count('id')
    ).order_by('-count')
    
    context = {
        'total_users': total_users,
        'new_users_week': new_users_week,
        'task_posters': task_posters,
        'task_doers': task_doers,
        'total_tasks': total_tasks,
        'open_tasks': open_tasks,
        'in_progress_tasks': in_progress_tasks,
        'completed_tasks': completed_tasks,
        'tasks_this_week': tasks_this_week,
        'total_revenue': total_revenue,
        'revenue_this_month': revenue_this_month,
        'pending_skills': pending_skills,
        'verified_skills': verified_skills,
        'recent_tasks': recent_tasks,
        'recent_users': recent_users,
        'pending_reports': pending_reports,
        'category_stats': category_stats,
    }
    
    return render(request, 'admin/dashboard.html', context)


@login_required
def admin_users(request):
    """Admin user management"""
    if request.user.role != 'admin':
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('dashboard')
    
    # Get filters
    role_filter = request.GET.get('role', '')
    search = request.GET.get('search', '')
    
    users = User.objects.all().order_by('-date_joined')
    
    if role_filter:
        users = users.filter(role=role_filter)
    
    if search:
        users = users.filter(
            Q(fullname__icontains=search) |
            Q(email__icontains=search) |
            Q(username__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(users, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'users': page_obj,
        'role_filter': role_filter,
        'search': search,
        'role_choices': User.ROLE_CHOICES
    }
    
    return render(request, 'admin/users.html', context)


@login_required
def admin_tasks(request):
    """Admin task management"""
    if request.user.role != 'admin':
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('dashboard')
    
    # Get filters
    status_filter = request.GET.get('status', '')
    category_filter = request.GET.get('category', '')
    search = request.GET.get('search', '')
    
    tasks = Task.objects.select_related('poster', 'doer').order_by('-created_at')
    
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    
    if category_filter:
        tasks = tasks.filter(category=category_filter)
    
    if search:
        tasks = tasks.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(poster__fullname__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(tasks, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'tasks': page_obj,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'search': search,
        'status_choices': Task.STATUS_CHOICES,
        'category_choices': Task.CATEGORY_CHOICES
    }
    
    return render(request, 'admin/tasks.html', context)


@login_required
def admin_skill_validation(request):
    """Admin skill validation management"""
    if request.user.role != 'admin':
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('dashboard')
    
    skills = StudentSkill.objects.select_related('student').order_by('-created_at')
    
    # Handle skill approval/rejection
    if request.method == 'POST':
        skill_id = request.POST.get('skill_id')
        action = request.POST.get('action')
        notes = request.POST.get('notes', '')
        
        try:
            skill = StudentSkill.objects.get(id=skill_id)
            
            if action == 'approve':
                skill.status = 'verified'
                skill.verified_by = request.user
                skill.verified_at = timezone.now()
                skill.notes = notes
                skill.save()
                
                # Create notification
                Notification.objects.create(
                    user=skill.student,
                    type='skill_verified',
                    title='Skill Verified!',
                    message=f'Your {skill.get_skill_name_display()} skill has been verified.',
                )
                
                messages.success(request, f"Approved {skill.student.fullname}'s {skill.get_skill_name_display()} skill.")
                
            elif action == 'reject':
                skill.status = 'rejected'
                skill.verified_by = request.user
                skill.verified_at = timezone.now()
                skill.notes = notes
                skill.save()
                
                # Create notification
                Notification.objects.create(
                    user=skill.student,
                    type='skill_verified',
                    title='Skill Validation Update',
                    message=f'Your {skill.get_skill_name_display()} skill validation was not approved. Please check the feedback and resubmit.',
                )
                
                messages.info(request, f"Rejected {skill.student.fullname}'s {skill.get_skill_name_display()} skill.")
                
        except StudentSkill.DoesNotExist:
            messages.error(request, "Skill not found.")
    
    # Filter pending skills
    pending_skills = skills.filter(status='pending')
    
    # Pagination
    paginator = Paginator(pending_skills, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'skills': page_obj,
        'total_pending': pending_skills.count()
    }
    
    return render(request, 'admin/skill_validation.html', context)


# ==================== API ENDPOINTS FOR ALGORITHMS ====================

@login_required
def api_auto_assign_task(request, task_id):
    """API endpoint to auto-assign a task to best matching agent"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    
    try:
        task = get_object_or_404(Task, id=task_id)
        
        # Check authorization - only task poster can assign
        if request.user != task.poster:
            return JsonResponse({'success': False, 'error': 'Only task poster can assign'}, status=403)
        
        # Check if task is open
        if task.status != 'open':
            return JsonResponse({'success': False, 'error': 'Task must be open to assign'}, status=400)
        
        # Auto-assign task
        assignment = auto_assign_task(task)
        
        if assignment:
            return JsonResponse({
                'success': True,
                'assignment_id': str(assignment.id),
                'agent_id': str(assignment.agent.id),
                'agent_name': assignment.agent.fullname,
                'match_score': float(assignment.total_match_score),
                'message': f'Task assigned to {assignment.agent.fullname}'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'No suitable agents available for this task'
            }, status=400)
        
    except Exception as e:
        logger.error(f"Error auto-assigning task: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def api_manual_assign_task(request, task_id):
    """API endpoint for manual task assignment by faculty"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    
    try:
        data = json.loads(request.body)
        agent_id = data.get('agent_id')
        notes = data.get('notes', '')
        
        task = get_object_or_404(Task, id=task_id)
        agent = get_object_or_404(User, id=agent_id, role='task_doer')
        
        # Check authorization
        if request.user != task.poster:
            return JsonResponse({'success': False, 'error': 'Only task poster can assign'}, status=403)
        
        # Check if task is open
        if task.status != 'open':
            return JsonResponse({'success': False, 'error': 'Task must be open'}, status=400)
        
        # Create manual assignment
        from .models import TaskAssignment
        
        assignment, created = TaskAssignment.objects.get_or_create(
            task=task,
            agent=agent,
            defaults={
                'assigned_by': request.user,
                'status': 'assigned',
                'assignment_method': 'manual',
                'assignment_notes': notes
            }
        )
        
        if not created:
            assignment.status = 'assigned'
            assignment.assignment_notes = notes
            assignment.save()
        
        # Send notification
        Notification.objects.create(
            user=agent,
            type='task_assigned',
            title='📋 Task Manually Assigned',
            message=f'You have been assigned to "{task.title}" by {request.user.fullname}',
            related_task=task
        )
        
        logger.info(f"Task {task_id} manually assigned to {agent.fullname}")
        
        return JsonResponse({
            'success': True,
            'assignment_id': str(assignment.id),
            'message': f'Task assigned to {agent.fullname}'
        })
        
    except Exception as e:
        logger.error(f"Error manually assigning task: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def api_reassign_task(request, assignment_id):
    """API endpoint to reassign a task to a different agent"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    
    try:
        data = json.loads(request.body)
        new_agent_id = data.get('agent_id')
        reason = data.get('reason', '')
        
        from .models import TaskAssignment
        
        assignment = get_object_or_404(TaskAssignment, id=assignment_id)
        new_agent = get_object_or_404(User, id=new_agent_id, role='task_doer')
        
        # Check authorization
        if request.user != assignment.task.poster:
            return JsonResponse({'success': False, 'error': 'Only task poster can reassign'}, status=403)
        
        # Mark current assignment as reassigned
        assignment.reassign(reason)
        
        # Create new assignment
        new_assignment = TaskAssignment.objects.create(
            task=assignment.task,
            agent=new_agent,
            assigned_by=request.user,
            status='assigned',
            assignment_method='manual',
            assignment_notes=f'Reassigned from {assignment.agent.fullname}. Reason: {reason}'
        )
        
        # Notify old agent
        Notification.objects.create(
            user=assignment.agent,
            type='task_reassigned',
            title='⚠️ Task Reassigned',
            message=f'Task "{assignment.task.title}" has been reassigned',
            related_task=assignment.task
        )
        
        # Notify new agent
        Notification.objects.create(
            user=new_agent,
            type='task_assigned',
            title='📋 Task Assigned',
            message=f'You have been assigned to "{assignment.task.title}"',
            related_task=assignment.task
        )
        
        logger.info(f"Task {assignment.task_id} reassigned from {assignment.agent.fullname} to {new_agent.fullname}")
        
        return JsonResponse({
            'success': True,
            'new_assignment_id': str(new_assignment.id),
            'message': f'Task reassigned to {new_agent.fullname}'
        })
        
    except Exception as e:
        logger.error(f"Error reassigning task: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def api_submit_feedback(request, task_id):
    """Submit rating and feedback for a completed task"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    
    try:
        data = json.loads(request.body)
        score = int(data.get('score', 0))
        feedback = data.get('feedback', '').strip()
        
        # Validate score
        if not (1 <= score <= 10):
            return JsonResponse({'success': False, 'error': 'Score must be between 1 and 10'}, status=400)
        
        task = get_object_or_404(Task, id=task_id)
        
        # Verify task is completed
        if task.status != 'completed':
            return JsonResponse({'success': False, 'error': 'Task must be completed'}, status=400)
        
        # Determine who is rating whom
        if request.user == task.poster:
            rated_user = task.doer
        elif request.user == task.doer:
            rated_user = task.poster
        else:
            return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
        
        if not rated_user:
            return JsonResponse({'success': False, 'error': 'Cannot rate: other party not assigned'}, status=400)
        
        # Check for existing rating
        existing_rating = Rating.objects.filter(
            task=task,
            rater=request.user,
            rated=rated_user
        ).first()
        
        if existing_rating:
            # Update existing rating
            existing_rating.score = score
            existing_rating.feedback = feedback
            existing_rating.save()
            action = 'updated'
        else:
            # Create new rating
            Rating.objects.create(
                task=task,
                rater=request.user,
                rated=rated_user,
                score=score,
                feedback=feedback
            )
            action = 'created'
        
        # Send notification to rated user
        Notification.objects.create(
            user=rated_user,
            type='rating_received',
            title=f'⭐ You received a {score}/10 rating',
            message=f'{request.user.fullname} rated you on "{task.title}"',
            related_task=task
        )
        
        logger.info(f"Rating {action} for task {task_id} by {request.user.fullname}")
        
        return JsonResponse({
            'success': True,
            'message': f'Feedback {action} successfully',
            'rating_id': str(existing_rating.id if existing_rating else Rating.objects.filter(task=task, rater=request.user).first().id)
        })
        
    except ValueError:
        return JsonResponse({'success': False, 'error': 'Invalid score value'}, status=400)
    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def api_get_task_feedback(request, task_id):
    """Get all feedback for a task"""
    try:
        task = get_object_or_404(Task, id=task_id)
        
        # Check authorization
        if request.user not in [task.poster, task.doer]:
            return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
        
        ratings = Rating.objects.filter(task=task).select_related('rater', 'rated')
        
        feedback_data = [{
            'id': str(rating.id),
            'rater_name': rating.rater.fullname,
            'rated_name': rating.rated.fullname,
            'score': rating.score,
            'feedback': rating.feedback,
            'created_at': rating.created_at.strftime('%B %d, %Y')
        } for rating in ratings]
        
        return JsonResponse({
            'success': True,
            'feedback': feedback_data,
            'count': len(feedback_data)
        })
        
    except Exception as e:
        logger.error(f"Error fetching feedback: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def api_payment_details(request, payment_id):
    """Get payment details for modal display"""
    try:
        from .models import Payment
        payment = get_object_or_404(Payment, id=payment_id)
        
        # Check authorization
        if request.user not in [payment.payer, payment.receiver]:
            return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
        
        return JsonResponse({
            'success': True,
            'payment': {
                'id': str(payment.id),
                'task_title': payment.task.title,
                'task_location': payment.task.location,
                'amount': str(payment.amount),
                'method': payment.method,
                'status': payment.status,
                'status_display': payment.get_status_display(),
                'created_at': payment.created_at.strftime('%B %d, %Y %I:%M %p'),
                'paymongo_id': payment.paymongo_payment_id or 'N/A',
                'reference_number': payment.reference_number or 'N/A'
            }
        })
    except Exception as e:
        logger.error(f"Error fetching payment details: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def api_download_receipt(request, payment_id):
    """Generate and download payment receipt as PDF"""
    try:
        from .models import Payment
        from django.http import HttpResponse
        from datetime import datetime
        
        payment = get_object_or_404(Payment, id=payment_id)
        
        # Check authorization
        if request.user not in [payment.payer, payment.receiver]:
            return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
        
        # Generate receipt text
        receipt_text = f"""
ERRANDEXPRESS PAYMENT RECEIPT
{'='*50}

Receipt Number: {payment.id}
Date: {payment.created_at.strftime('%B %d, %Y %I:%M %p')}

TRANSACTION DETAILS
{'='*50}
Task: {payment.task.title}
Location: {payment.task.location}
Category: {payment.task.get_category_display()}

PAYMENT INFORMATION
{'='*50}
Amount: ₱{payment.amount:,.2f}
Method: {payment.get_method_display()}
Status: {payment.get_status_display()}
Reference: {payment.reference_number or 'N/A'}
PayMongo ID: {payment.paymongo_payment_id or 'N/A'}

PARTIES INVOLVED
{'='*50}
Payer: {payment.payer.fullname}
Receiver: {payment.receiver.fullname}

NOTES
{'='*50}
{payment.notes or 'No additional notes'}

{'='*50}
This is an automated receipt. Please keep for your records.
For inquiries, contact ErrandExpress Support.
"""
        
        # Create response
        response = HttpResponse(receipt_text, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="receipt_{payment.id}.txt"'
        return response
        
    except Exception as e:
        logger.error(f"Error generating receipt: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def api_check_chat_access(request, task_id):
    """API endpoint to check chat access for a task"""
    access_result = check_chat_access(task_id, request.user)
    return JsonResponse(access_result)


@login_required  
def api_unlock_chat_after_payment(request, task_id):
    """API endpoint called by PayMongo webhook to unlock chat after payment"""
    if request.method == 'POST':
        try:
            task = Task.objects.get(id=task_id)
            
            # Update commission status
            commission = task.commission
            commission.status = 'paid'
            commission.paid_at = timezone.now()
            commission.save()
            
            # Unlock chat
            task.chat_unlocked = True
            task.save()
            
            # Create notification
            Notification.objects.create(
                user=task.poster,
                type='payment_confirmed',
                title='Payment Confirmed',
                message=f'₱2 system fee paid. Chat unlocked for "{task.title}"',
                related_task=task
            )
            
            return JsonResponse({
                'success': True, 
                'message': 'Chat unlocked successfully',
                'chat_unlocked': True
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
@require_http_methods(["POST"])
def api_send_message(request):
    """API endpoint for sending messages via AJAX (used by standalone chat)"""
    import json
    from django.db.models import Count
    
    try:
        data = json.loads(request.body)
        task_id = data.get('task_id')
        message_content = data.get('message', '').strip()
        
        if not task_id or not message_content:
            return JsonResponse({'success': False, 'error': 'Missing required fields'})
        
        # Optimize: Use select_related to fetch task with poster/doer in one query
        task = Task.objects.select_related('poster', 'doer').get(id=task_id)
        
        # Check if user can send messages
        if request.user not in [task.poster, task.doer]:
            return JsonResponse({'success': False, 'error': 'Not authorized'})
        
        # Optimize: Count messages with aggregation (single query)
        message_count = Message.objects.filter(task=task).aggregate(Count('id'))['id__count']
        
        # Check 5-message limit BEFORE allowing message creation
        # If 5 messages already exist and chat is not unlocked, block immediately
        if message_count >= 5 and not task.chat_unlocked:
            return JsonResponse({
                'success': False, 
                'error': 'You have reached the 5-message limit. Please pay ₱2 system fee to continue chatting.',
                'payment_required': True
            })
        
        # Create message
        message = Message.objects.create(
            task=task,
            sender=request.user,
            message=message_content
        )
        
        # Create notification for the other party (defer to background to avoid blocking response)
        # This is done asynchronously to keep message sending fast
        try:
            recipient = task.doer if task.poster == request.user else task.poster
            if recipient:
                # Use on_commit to defer notification creation until after transaction commits
                from django.db import transaction
                transaction.on_commit(lambda: Notification.objects.create(
                    user=recipient,
                    type='system_message',
                    title=f'New message in "{task.title}"',
                    message=f'{request.user.fullname} sent you a message.',
                    related_task=task
                ))
        except Exception as e:
            logger.warning(f"Failed to create notification: {str(e)}")
        
        # Calculate remaining messages
        messages_remaining = max(0, 5 - message_count - 1) if message_count < 5 else None
        
        return JsonResponse({
            'success': True,
            'message_id': str(message.id),
            'created_at': message.created_at.isoformat(),
            'sender': request.user.fullname,
            'messages_remaining': messages_remaining
        })
        
    except Task.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Task not found'})
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'})
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        return JsonResponse({'success': False, 'error': 'Failed to send message'})


@login_required
def api_get_messages(request, task_id):
    """API endpoint to fetch messages for a task (for polling) - OPTIMIZED"""
    try:
        task = get_object_or_404(Task, id=task_id)
        
        # Check if user can access messages
        if request.user not in [task.poster, task.doer]:
            return JsonResponse({'success': False, 'error': 'Not authorized'})
        
        # Optimize: Only fetch last 20 messages (not 50) to reduce payload
        # Most polling requests will only need 1-2 new messages
        messages = Message.objects.filter(task=task).select_related('sender').order_by('-created_at')[:20]
        messages = list(reversed(messages))  # Reverse to get chronological order
        
        # Serialize messages with minimal data
        messages_data = [{
            'id': str(msg.id),
            'sender_id': str(msg.sender.id),
            'sender_name': msg.sender.fullname,
            'message': msg.message,
            'created_at': msg.created_at.isoformat()
        } for msg in messages]
        
        return JsonResponse({
            'success': True,
            'messages': messages_data,
            'count': len(messages_data)
        })
        
    except Exception as e:
        logger.error(f"Error fetching messages: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})


# ==================== PAYMONGO LIVE INTEGRATION ====================

def make_paymongo_request(endpoint, payload, max_retries=3):
    """
    Helper function to make PayMongo API requests with retry logic
    """
    import time
    
    secret_key = settings.PAYMONGO_SECRET_KEY
    auth_header = base64.b64encode(f"{secret_key}:".encode()).decode()
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Basic {auth_header}"
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.post(
                f"https://api.paymongo.com/v1{endpoint}",
                headers=headers,
                data=json.dumps(payload),
                timeout=10
            )
            
            if response.status_code == 200:
                return response
            elif response.status_code >= 500 and attempt < max_retries - 1:
                # Server error, retry with exponential backoff
                wait_time = 2 ** attempt
                logger.warning(f"PayMongo server error, retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                continue
            else:
                return response
                
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                logger.warning(f"PayMongo timeout, retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
            else:
                raise
        except requests.exceptions.ConnectionError:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                logger.warning(f"PayMongo connection error, retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
            else:
                raise
    
    return None


@csrf_exempt
def create_payment_intent(request):
    """
    💸 Create a ₱2 commission payment intent (GCash or Card)
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    
    try:
        # Check if PayMongo keys are configured
        if not settings.PAYMONGO_SECRET_KEY:
            logger.error("PayMongo secret key not configured")
            return JsonResponse({'error': 'Payment gateway not configured. Please set PAYMONGO_SECRET_KEY.'}, status=500)
        
        data = json.loads(request.body)
        task_id = data.get('task_id')
        payment_method = data.get('payment_method', 'gcash')
        amount = 200  # ₱2 = 200 centavos

        # For card payments, return card form flag
        if payment_method == 'card':
            logger.info(f"Card payment requested for task {task_id}")
            return JsonResponse({
                "success": True,
                "checkout_url": f"/payments/card-form/{task_id}/",
                "is_card_form": True
            })

        # For GCash, create payment intent
        payload = {
            "data": {
                "attributes": {
                    "amount": amount,
                    "currency": "PHP",
                    "description": f"ErrandExpress ₱2 Fee for Task {task_id}",
                    "payment_method_allowed": ["gcash"],
                    "statement_descriptor": "ERRANDEXPRESS"
                }
            }
        }

        response = make_paymongo_request("/payment_intents", payload)
        
        if response and response.status_code == 200:
            logger.info(f"Payment intent created for task {task_id}: {response.status_code}")
            return JsonResponse(response.json())
        else:
            error_msg = response.text if response else "Unknown error"
            logger.error(f"Payment intent creation failed: {error_msg}")
            return JsonResponse({'error': f'Payment creation failed: {error_msg}'}, status=500)
        
    except Exception as e:
        logger.error(f"Payment intent creation failed: {str(e)}")
        return JsonResponse({'error': f'Payment error: {str(e)}'}, status=500)


@csrf_exempt
def create_gcash_payment(request):
    """
    💳 Create the actual GCash payment source using the intent (LIVE)
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    
    try:
        data = json.loads(request.body)
        task_id = data.get('task_id')
        client_key = data.get('client_key')
        
        if not client_key:
            logger.error("Missing client_key for GCash payment")
            return JsonResponse({'error': 'Missing client_key from payment intent'}, status=400)
        
        payload = {
            "data": {
                "attributes": {
                    "type": "gcash",
                    "amount": 200,  # ₱2 = 200 centavos
                    "currency": "PHP",
                    "redirect": {
                        "success": f"{request.build_absolute_uri('/payment/success/')}?task_id={task_id}",
                        "failed": f"{request.build_absolute_uri('/payment/failed/')}?task_id={task_id}"
                    }
                }
            }
        }

        # Use live secret key
        secret_key = settings.PAYMONGO_SECRET_KEY
        auth_header = base64.b64encode(f"{secret_key}:".encode()).decode()

        response = requests.post(
            "https://api.paymongo.com/v1/sources",
            headers={
                "accept": "application/json",
                "content-type": "application/json",
                "authorization": f"Basic {auth_header}"
            },
            data=json.dumps(payload)
        )

        if response.status_code == 200:
            result = response.json()
            checkout_url = result["data"]["attributes"]["redirect"]["checkout_url"]
            
            logger.info(f"GCash payment created for task {task_id}: {checkout_url}")
            return JsonResponse({
                "success": True,
                "checkout_url": checkout_url,
                "source_id": result["data"]["id"]
            })
        else:
            logger.error(f"GCash payment creation failed: {response.text}")
            return JsonResponse({'error': 'Payment creation failed'}, status=500)
            
    except Exception as e:
        logger.error(f"GCash payment creation error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def create_card_payment(request):
    """
    💳 Create card payment form for testing with PayMongo test card
    Test Card: 4343434343434345, Any future expiry, Any CVC
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    
    try:
        data = json.loads(request.body)
        task_id = data.get('task_id')
        
        # Get task
        task = Task.objects.get(id=task_id)
        
        # Return card payment form instead of checkout URL
        # The form will use the test endpoint to confirm payment
        context = {
            'task': task,
            'amount': 2.00,
            'task_id': task_id
        }
        
        logger.info(f"Card payment form requested for task {task_id}")
        
        # Return success with a special flag to render the form on frontend
        return JsonResponse({
            "success": True,
            "checkout_url": f"/payments/card-form/{task_id}/",  # Frontend will handle this
            "is_card_form": True
        })
            
    except Task.DoesNotExist:
        logger.error(f"Task not found: {task_id}")
        return JsonResponse({'error': 'Task not found'}, status=404)
    except Exception as e:
        logger.error(f"Card payment creation error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def card_payment_form(request, task_id):
    """
    💳 Display card payment form for testing
    """
    try:
        task = Task.objects.get(id=task_id)
        
        context = {
            'task': task,
            'amount': 2.00,
        }
        
        return render(request, 'payments/card_payment.html', context)
        
    except Task.DoesNotExist:
        messages.error(request, 'Task not found')
        return redirect('messages_list')


@login_required
def test_confirm_payment(request, task_id):
    """
    🧪 TEST ENDPOINT: Manually confirm payment for testing
    Only available in DEBUG mode for testing purposes
    """
    if not settings.DEBUG:
        return JsonResponse({'error': 'Not available in production'}, status=403)
    
    try:
        from .models import Task, SystemCommission
        
        task = Task.objects.get(id=task_id)
        
        # Unlock chat
        task.chat_unlocked = True
        task.save()
        
        # Update SystemCommission if exists
        try:
            commission = SystemCommission.objects.get(task=task)
            commission.status = 'paid'
            commission.save()
            logger.info(f"Test: SystemCommission marked as paid for task {task_id}")
        except SystemCommission.DoesNotExist:
            logger.warning(f"Test: No SystemCommission found for task {task_id}")
        
        # Create notification
        from .models import Notification
        Notification.objects.create(
            user=task.poster,
            title='Test Payment Confirmed',
            message=f'Test payment for task "{task.title}" has been confirmed. Chat is now unlocked.',
            type='payment_received',
            related_task=task
        )
        
        logger.info(f"Test payment confirmed for task {task_id}")
        return JsonResponse({'success': True, 'message': 'Test payment confirmed! Chat unlocked.'})
        
    except Task.DoesNotExist:
        return JsonResponse({'error': 'Task not found'}, status=404)
    except Exception as e:
        logger.error(f"Test payment confirmation error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def paymongo_webhook(request):
    """
    🔔 COMPREHENSIVE PAYMENT WEBHOOK HANDLER
    Handles both ₱2 system fees and main task payments
    
    STEP 3 & STEP 5B: PayMongo webhook processing
    Includes webhook signature verification for security
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    
    try:
        # 🔐 VERIFY WEBHOOK SIGNATURE
        webhook_secret = settings.PAYMONGO_WEBHOOK_SECRET
        if webhook_secret:
            # Get signature from header
            signature = request.headers.get('X-Paymongo-Signature', '')
            
            # Calculate expected signature
            body = request.body
            expected_signature = hmac.new(
                webhook_secret.encode(),
                body,
                hashlib.sha256
            ).hexdigest()
            
            # Verify signature
            if not hmac.compare_digest(signature, expected_signature):
                logger.error(f"❌ Invalid webhook signature. Expected: {expected_signature}, Got: {signature}")
                return JsonResponse({'error': 'Invalid signature'}, status=401)
            
            logger.info(f"✅ Webhook signature verified")
        else:
            logger.warning("⚠️ PAYMONGO_WEBHOOK_SECRET not configured - skipping signature verification")
        
        event = json.loads(request.body)
        event_type = event["data"]["attributes"]["type"]
        
        logger.info(f"🔔 PayMongo webhook received: {event_type}")
        logger.info(f"Webhook payload: {json.dumps(event, indent=2)}")
        
        if event_type == "payment.paid":
            # Extract information from payment description
            description = event["data"]["attributes"]["data"]["attributes"]["description"]
            amount_centavos = event["data"]["attributes"]["data"]["attributes"]["amount"]
            amount_pesos = amount_centavos / 100
            source_id = event["data"]["attributes"]["data"]["id"]
            
            logger.info(f"💰 Payment received: ₱{amount_pesos} - Description: {description}")
            logger.info(f"Source ID: {source_id}")
            
            from .models import Task, SystemCommission, Payment
            
            # 🔹 STEP 3: ₱2 System Fee Payment
            if "System Fee" in description or amount_pesos == 2.0:
                logger.info("📝 Processing as SYSTEM FEE payment")
                
                # Extract task ID from description
                # Format: "ErrandExpress System Fee - Task Title" or "ErrandExpress System Fee - {task_id}"
                try:
                    # Try to extract UUID from description
                    import re
                    uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
                    match = re.search(uuid_pattern, description)
                    
                    if match:
                        task_id = match.group(0)
                    else:
                        # Fallback: try to get from last part
                        task_id = description.split(" ")[-1]
                    
                    logger.info(f"Extracted task_id: {task_id}")
                    
                    task = Task.objects.get(id=task_id)
                    commission = SystemCommission.objects.get(task=task)
                    
                    # Mark ₱2 commission as paid
                    commission.status = 'paid'
                    commission.paid_at = timezone.now()
                    commission.paymongo_payment_id = source_id
                    commission.save()
                    
                    # 💰 ADD REVENUE TO SYSTEM WALLET
                    from .models import SystemWallet
                    wallet = SystemWallet.get_or_create_wallet()
                    wallet.add_revenue(
                        amount=amount_pesos,
                        description=f"System fee from task: {task.title}"
                    )
                    logger.info(f"💰 Revenue added to wallet: ₱{amount_pesos}")
                    
                    # 🔔 UNLOCK CHAT AUTOMATICALLY
                    task.chat_unlocked = True
                    task.save()
                    
                    # Notify poster
                    Notification.objects.create(
                        user=task.poster,
                        type='payment_confirmed',
                        title='₱2 System Fee Paid! 💳',
                        message=f'System fee paid successfully. Chat unlocked for "{task.title}"',
                        related_task=task
                    )
                    
                    logger.info(f"✅ System fee payment CONFIRMED - chat unlocked for task {task_id}")
                    
                except (Task.DoesNotExist, SystemCommission.DoesNotExist) as e:
                    logger.error(f"❌ Task or commission not found for ₱2 payment. Task ID: {task_id}, Error: {str(e)}")
                except Exception as e:
                    logger.error(f"❌ Error processing system fee payment: {str(e)}")
            
            # 🔹 STEP 5B: Task Doer Payment (GCash/Card) - NEW
            elif "Task Payment" in description or ("ErrandExpress Task Payment" in description):
                logger.info("📝 Processing as TASK DOER PAYMENT")
                
                # Extract task ID and payment ID from description
                try:
                    import re
                    uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
                    matches = re.findall(uuid_pattern, description)
                    
                    task_id = None
                    payment_id = None
                    
                    if len(matches) >= 2:
                        task_id = matches[0]
                        payment_id = matches[1]
                    elif len(matches) == 1:
                        task_id = matches[0]
                    else:
                        # Fallback: try to extract from quotes
                        task_id = description.split('"')[1] if '"' in description else description.split(" ")[-1]
                    
                    logger.info(f"Extracted task_id: {task_id}, payment_id: {payment_id}")
                    
                    task = Task.objects.get(id=task_id)
                    
                    # Try to get existing payment by ID first
                    if payment_id:
                        try:
                            payment = Payment.objects.get(id=payment_id)
                            logger.info(f"Found existing payment record: {payment_id}")
                        except Payment.DoesNotExist:
                            logger.warning(f"Payment ID {payment_id} not found, creating new record")
                            payment = None
                    else:
                        payment = None
                    
                    # If no payment found, try to get by task
                    if not payment:
                        try:
                            payment = Payment.objects.get(task=task, status='pending_payment')
                            logger.info(f"Found pending payment for task: {payment.id}")
                        except Payment.DoesNotExist:
                            logger.warning(f"No pending payment found for task, creating new record")
                            payment = None
                    
                    # Create payment if it doesn't exist
                    if not payment:
                        payment = Payment.objects.create(
                            task=task,
                            payer=task.poster,
                            receiver=task.doer,
                            amount=task.price,
                            method='gcash',
                            status='pending_payment'
                        )
                        logger.info(f"Created new payment record: {payment.id}")
                    
                    # Mark task doer payment as paid
                    payment.status = 'paid'
                    payment.paid_at = timezone.now()
                    payment.paymongo_source_id = source_id
                    payment.save()
                    
                    logger.info(f"✅ Payment record updated: {payment.id}, status=paid")
                    
                    # 💰 ADD COMMISSION TO SYSTEM WALLET
                    from .models import SystemWallet
                    wallet = SystemWallet.get_or_create_wallet()
                    from decimal import Decimal
                    commission_amount = Decimal(str(task.price)) * Decimal('0.10')
                    wallet.add_revenue(
                        amount=commission_amount,
                        description=f"Commission from task payment: {task.title}"
                    )
                    logger.info(f"💰 Commission added to wallet: ₱{commission_amount}")
                    
                    # Complete the task
                    task.status = 'completed'
                    task.completed_at = timezone.now()
                    task.save()
                    logger.info(f"✅ Task marked as completed: {task_id}")
                    
                    # Notify task doer about payment
                    Notification.objects.create(
                        user=task.doer,
                        type='payment_received',
                        title='Payment Received! 💰',
                        message=f'You received ₱{amount_pesos} for completing "{task.title}". Task poster can now rate you.',
                        related_task=task
                    )
                    logger.info(f"✅ Notification sent to task doer {task.doer.id}")
                    
                    # Notify task poster that payment is confirmed
                    Notification.objects.create(
                        user=task.poster,
                        type='payment_confirmed',
                        title='Task Doer Payment Confirmed! 💳',
                        message=f'Payment of ₱{amount_pesos} sent to {task.doer.fullname}. You can now rate them.',
                        related_task=task
                    )
                    logger.info(f"✅ Notification sent to task poster {task.poster.id}")
                    
                    logger.info(f"✅ Task doer payment CONFIRMED - task {task_id} payment verified")
                    
                except Task.DoesNotExist:
                    logger.error(f"❌ Task not found for payment: {task_id}")
                except Exception as e:
                    logger.error(f"❌ Error processing task doer payment: {str(e)}", exc_info=True)
            
            # 🔹 STEP 5B: Main Task Payment (GCash) - OLD
            elif "Task payment" in description or (amount_pesos > 2.0 and amount_pesos < 100000):
                logger.info("📝 Processing as LEGACY TASK PAYMENT")
                
                # Extract task ID from description
                try:
                    import re
                    uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
                    match = re.search(uuid_pattern, description)
                    
                    if match:
                        task_id = match.group(0)
                    else:
                        # Fallback: try to extract from quotes
                        task_id = description.split('"')[1] if '"' in description else description.split(" ")[-1]
                    
                    logger.info(f"Extracted task_id: {task_id}")
                    
                    # Find the pending payment record
                    payment = Payment.objects.get(
                        task__id=task_id,
                        method='gcash',
                        status='pending_payment'
                    )
                    
                    # Mark main task payment as paid
                    payment.status = 'paid'
                    payment.paid_at = timezone.now()
                    payment.paymongo_payment_id = source_id
                    payment.save()
                    
                    # 🔔 COMPLETE TASK AUTOMATICALLY
                    task = payment.task
                    task.status = 'completed'
                    task.completed_at = timezone.now()
                    task.save()
                    
                    # Notify both users
                    Notification.objects.create(
                        user=payment.poster,
                        type='payment_confirmed',
                        title='Task Payment Confirmed! 💰',
                        message=f'GCash payment of ₱{amount_pesos} confirmed. Task "{task.title}" completed!',
                        related_task=task
                    )
                    
                    Notification.objects.create(
                        user=payment.doer,
                        type='payment_received',
                        title='Payment Received! 🎉',
                        message=f'You received ₱{amount_pesos} for task "{task.title}". Task completed!',
                        related_task=task
                    )
                    
                    # 🔹 STEP 6: Prompt for ratings
                    Notification.objects.create(
                        user=payment.poster,
                        type='rate_reminder',
                        title='Please Rate Your Doer',
                        message=f'Task "{task.title}" completed. Please rate {payment.doer.fullname}.',
                        related_task=task
                    )
                    
                    Notification.objects.create(
                        user=payment.doer,
                        type='rate_reminder',
                        title='Please Rate Your Poster',
                        message=f'Task "{task.title}" completed. Please rate {payment.poster.fullname}.',
                        related_task=task
                    )
                    
                    logger.info(f"✅ Task payment CONFIRMED - task {task_id} completed automatically")
                    
                except Payment.DoesNotExist:
                    logger.error(f"❌ Payment record not found for task payment: {task_id}")
                except Task.DoesNotExist:
                    logger.error(f"❌ Task not found for payment: {task_id}")
                except Exception as e:
                    logger.error(f"❌ Error processing task payment: {str(e)}")
        
        elif event_type == "source.chargeable":
            # Handle GCash payment source creation
            logger.info("🔔 GCash payment source is chargeable")
        
        return JsonResponse({"status": "received"})
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ Invalid JSON in webhook: {str(e)}")
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"❌ Webhook processing error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def test_paymongo_integration(request):
    """Test page for PayMongo live integration"""
    if request.user.role != 'admin':
        messages.error(request, "Only admins can access the test page.")
        return redirect('dashboard')
    
    context = {
        'paymongo_public_key': settings.PAYMONGO_PUBLIC_KEY,
        'paymongo_secret_key': settings.PAYMONGO_SECRET_KEY,
    }
    
    return render(request, 'payments/test_payment.html', context)


# ==================== TASK COMPLETION PAYMENT ENDPOINTS ====================

@csrf_exempt
@login_required
def api_complete_task_payment(request, task_id):
    """
    💸 API: Initiate task completion payment (STEP 5)
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    
    try:
        data = json.loads(request.body)
        payment_method = data.get('payment_method', 'gcash')
        
        result = handle_task_completion_payment(task_id, request.user, payment_method)
        
        if result['success']:
            return JsonResponse(result)
        else:
            return JsonResponse(result, status=400)
            
    except Exception as e:
        logger.error(f"Task completion payment API error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@login_required
def api_confirm_cod_payment(request, payment_id):
    """
    💵 API: Confirm COD payment received (STEP 5A)
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    
    try:
        result = confirm_cod_payment(payment_id, request.user)
        
        if result['success']:
            return JsonResponse(result)
        else:
            return JsonResponse(result, status=400)
            
    except Exception as e:
        logger.error(f"COD confirmation API error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def create_task_payment_intent(request):
    """
    💳 Create PayMongo payment intent for main task payment (STEP 5B)
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    
    try:
        data = json.loads(request.body)
        payment_id = data.get('payment_id')
        
        # Get payment record
        from .models import Payment
        payment = Payment.objects.get(id=payment_id, status='pending_payment')
        
        amount_centavos = int(float(payment.amount) * 100)  # Convert to centavos
        
        payload = {
            "data": {
                "attributes": {
                    "amount": amount_centavos,
                    "currency": "PHP",
                    "description": f'Task payment for "{payment.task.title}"',
                    "payment_method_allowed": ["gcash", "card"],
                    "statement_descriptor": "ERRANDEXPRESS"
                }
            }
        }

        # Use live secret key
        secret_key = settings.PAYMONGO_SECRET_KEY
        auth_header = base64.b64encode(f"{secret_key}:".encode()).decode()

        response = requests.post(
            "https://api.paymongo.com/v1/payment_intents",
            headers={
                "accept": "application/json",
                "content-type": "application/json",
                "authorization": f"Basic {auth_header}"
            },
            data=json.dumps(payload)
        )

        logger.info(f"Task payment intent created for payment {payment_id}: ₱{payment.amount}")
        return JsonResponse(response.json())
        
    except Payment.DoesNotExist:
        return JsonResponse({'error': 'Payment not found'}, status=404)
    except Exception as e:
        logger.error(f"Task payment intent creation failed: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def create_task_gcash_payment(request):
    """
    💳 Create GCash payment source for main task payment (STEP 5B)
    Integrated with PayMongo webhook for automatic confirmation
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    
    try:
        data = json.loads(request.body)
        payment_id = data.get('payment_id')
        
        if not payment_id:
            logger.error("Missing payment_id in request")
            return JsonResponse({'error': 'Missing payment_id'}, status=400)
        
        # Get payment record
        from .models import Payment
        try:
            payment = Payment.objects.get(id=payment_id, status='pending_payment')
        except Payment.DoesNotExist:
            logger.error(f"Payment not found: {payment_id}")
            return JsonResponse({'error': 'Payment not found'}, status=404)
        
        # Validate amount
        amount_centavos = int(float(payment.amount) * 100)
        if amount_centavos <= 0:
            logger.error(f"Invalid payment amount: {payment.amount}")
            return JsonResponse({'error': 'Invalid payment amount'}, status=400)
        
        # Build redirect URLs
        success_url = request.build_absolute_uri(reverse('payment_success'))
        failed_url = request.build_absolute_uri(reverse('payment_failed'))
        
        # Add payment_id to query params for webhook tracking
        success_url = f"{success_url}?payment_id={payment_id}"
        failed_url = f"{failed_url}?payment_id={payment_id}"
        
        logger.info(f"Creating GCash payment: payment_id={payment_id}, amount={amount_centavos} centavos (₱{payment.amount})")
        logger.info(f"Success URL: {success_url}")
        logger.info(f"Failed URL: {failed_url}")
        
        payload = {
            "data": {
                "attributes": {
                    "type": "gcash",
                    "amount": amount_centavos,
                    "currency": "PHP",
                    "description": f"Task Payment - {payment.task.title} (ID: {payment_id})",
                    "redirect": {
                        "success": success_url,
                        "failed": failed_url
                    }
                }
            }
        }

        # Use live secret key
        secret_key = settings.PAYMONGO_SECRET_KEY
        if not secret_key:
            logger.error("PAYMONGO_SECRET_KEY not configured")
            return JsonResponse({'error': 'Payment service not configured'}, status=500)
        
        auth_header = base64.b64encode(f"{secret_key}:".encode()).decode()

        logger.info(f"Payload: {json.dumps(payload, indent=2)}")

        response = requests.post(
            "https://api.paymongo.com/v1/sources",
            headers={
                "accept": "application/json",
                "content-type": "application/json",
                "authorization": f"Basic {auth_header}"
            },
            json=payload,
            timeout=10
        )

        logger.info(f"PayMongo response status: {response.status_code}")
        logger.info(f"PayMongo response: {response.text}")

        if response.status_code == 200:
            result = response.json()
            try:
                checkout_url = result["data"]["attributes"]["redirect"]["checkout_url"]
                source_id = result["data"]["id"]
                
                # Store source_id in payment record for webhook tracking
                payment.paymongo_source_id = source_id
                payment.save()
                
                logger.info(f"✅ Task GCash payment created: payment_id={payment_id}, source_id={source_id}, checkout_url={checkout_url}")
                return JsonResponse({
                    "success": True,
                    "checkout_url": checkout_url,
                    "source_id": source_id,
                    "amount": float(payment.amount),
                    "payment_id": str(payment_id)
                })
            except KeyError as e:
                logger.error(f"Invalid PayMongo response structure: {str(e)}")
                logger.error(f"Full response: {result}")
                return JsonResponse({'error': 'Invalid payment response'}, status=500)
        else:
            logger.error(f"❌ Task GCash payment creation failed: Status={response.status_code}")
            logger.error(f"Response: {response.text}")
            return JsonResponse({'error': f'Payment creation failed: {response.status_code}'}, status=400)
            
    except json.JSONDecodeError:
        logger.error("Invalid JSON in request body")
        return JsonResponse({'error': 'Invalid request format'}, status=400)
    except Exception as e:
        logger.error(f"Task GCash payment creation error: {str(e)}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def create_task_card_payment(request):
    """
    💳 Create card payment source for main task payment (STEP 5B)
    Test Card: 4343434343434345, Any future expiry, Any CVC
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    
    try:
        data = json.loads(request.body)
        payment_id = data.get('payment_id')
        
        # Get payment record
        from .models import Payment
        payment = Payment.objects.get(id=payment_id, status='pending_payment')
        
        amount_centavos = int(float(payment.amount) * 100)
        
        payload = {
            "data": {
                "attributes": {
                    "type": "card",
                    "amount": amount_centavos,
                    "currency": "PHP",
                    "redirect": {
                        "success": f"{request.build_absolute_uri('/payment/success/')}?payment_id={payment_id}",
                        "failed": f"{request.build_absolute_uri('/payment/failed/')}?payment_id={payment_id}"
                    }
                }
            }
        }

        # Use live secret key
        secret_key = settings.PAYMONGO_SECRET_KEY
        auth_header = base64.b64encode(f"{secret_key}:".encode()).decode()

        response = requests.post(
            "https://api.paymongo.com/v1/sources",
            headers={
                "accept": "application/json",
                "content-type": "application/json",
                "authorization": f"Basic {auth_header}"
            },
            data=json.dumps(payload)
        )

        if response.status_code == 200:
            result = response.json()
            checkout_url = result["data"]["attributes"]["redirect"]["checkout_url"]
            
            logger.info(f"Task card payment created for payment {payment_id}: ₱{payment.amount}")
            return JsonResponse({
                "success": True,
                "checkout_url": checkout_url,
                "source_id": result["data"]["id"],
                "amount": float(payment.amount)
            })
        else:
            logger.error(f"Task card payment creation failed: {response.text}")
            return JsonResponse({'error': 'Payment creation failed'}, status=500)
            
    except Payment.DoesNotExist:
        return JsonResponse({'error': 'Payment not found'}, status=404)
    except Exception as e:
        logger.error(f"Task card payment creation error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


# ==================== PROFILE & USER MANAGEMENT ====================

@login_required
def profile(request):
    """User profile page with edit functionality"""
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'delete_profile_picture':
            # Delete profile picture
            if request.user.profile_picture:
                request.user.profile_picture.delete()
                request.user.save()
                messages.success(request, 'Profile picture deleted successfully')
            return redirect('profile')
        
        elif action == 'change_password':
            # Handle password change
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            if not request.user.check_password(current_password):
                messages.error(request, 'Current password is incorrect')
            elif new_password != confirm_password:
                messages.error(request, 'New passwords do not match')
            elif len(new_password) < 8:
                messages.error(request, 'Password must be at least 8 characters')
            else:
                request.user.set_password(new_password)
                request.user.save()
                messages.success(request, 'Password updated successfully')
                return redirect('profile')
        else:
            # Handle profile update
            fullname = request.POST.get('fullname')
            phone = request.POST.get('phone')
            bio = request.POST.get('bio')
            
            # Only update fields if they are provided
            if fullname:
                request.user.fullname = fullname
            if phone:
                request.user.phone_number = phone
            if bio:
                request.user.bio = bio
            
            # Handle profile picture upload with compression
            if 'profile_picture' in request.FILES:
                profile_pic = request.FILES['profile_picture']
                # Compress image before saving
                compressed_pic = compress_profile_picture(profile_pic)
                request.user.profile_picture = compressed_pic
            
            request.user.save()
            
            messages.success(request, 'Profile updated successfully')
            return redirect('profile')
    
    # Get real user statistics
    from django.db.models import Avg, Count, Sum
    
    # Tasks completed
    if request.user.role == 'task_doer':
        tasks_completed = Task.objects.filter(doer=request.user, status='completed').count()
        total_earned = Payment.objects.filter(receiver=request.user, status='confirmed').aggregate(Sum('amount'))['amount__sum'] or 0
    else:
        tasks_completed = Task.objects.filter(poster=request.user, status='completed').count()
        total_earned = 0
    
    # User rating
    user_rating = Rating.objects.filter(rated=request.user).aggregate(Avg('score'))['score__avg']
    if user_rating:
        user_rating = round(user_rating, 1)
    else:
        user_rating = 0
    
    # Verified skills
    verified_skills = StudentSkill.objects.filter(student=request.user, status='verified')
    
    # Recent activity (last 5 tasks)
    if request.user.role == 'task_doer':
        recent_tasks = Task.objects.filter(doer=request.user).order_by('-accepted_at')[:5]
    else:
        recent_tasks = Task.objects.filter(poster=request.user).order_by('-created_at')[:5]
    
    return render(request, 'profile.html', {
        'user': request.user,
        'tasks_completed': tasks_completed,
        'user_rating': user_rating,
        'total_earned': total_earned,
        'verified_skills': verified_skills,
        'recent_tasks': recent_tasks,
    })


@login_required
def system_wallet(request):
    """System wallet showing platform revenue (Admin only)"""
    if request.user.role != 'admin':
        messages.error(request, 'Access denied. Admin only.')
        return redirect('dashboard')
    
    from .models import SystemCommission
    from django.db.models import Sum, Count
    from datetime import datetime, timedelta
    
    # Get all commissions
    all_commissions = SystemCommission.objects.all()
    
    # Total revenue (paid commissions)
    paid_commissions = all_commissions.filter(status='paid')
    total_revenue = paid_commissions.aggregate(total=Sum('amount'))['total'] or 0
    total_commissions_count = paid_commissions.count()
    
    # Monthly revenue
    current_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_commissions = paid_commissions.filter(paid_at__gte=current_month)
    monthly_revenue = monthly_commissions.aggregate(total=Sum('amount'))['total'] or 0
    monthly_commissions_count = monthly_commissions.count()
    
    # Pending revenue
    pending_commissions = all_commissions.filter(status='unpaid')
    pending_revenue = pending_commissions.aggregate(total=Sum('amount'))['total'] or 0
    pending_commissions_count = pending_commissions.count()
    
    # Recent transactions
    recent_commissions = all_commissions.select_related('task', 'task__poster').order_by('-created_at')[:20]
    
    # Statistics
    active_users = User.objects.filter(is_active=True).count()
    completed_tasks = Task.objects.filter(status='completed').count()
    total_tasks = Task.objects.exclude(status='open').count()
    success_rate = round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1)
    avg_transaction = round(total_revenue / total_commissions_count, 2) if total_commissions_count > 0 else 0
    
    return render(request, 'system_wallet.html', {
        'total_revenue': total_revenue,
        'total_commissions': total_commissions_count,
        'monthly_revenue': monthly_revenue,
        'monthly_commissions': monthly_commissions_count,
        'pending_revenue': pending_revenue,
        'pending_commissions': pending_commissions_count,
        'recent_commissions': recent_commissions,
        'active_users': active_users,
        'completed_tasks': completed_tasks,
        'success_rate': success_rate,
        'avg_transaction': avg_transaction,
    })


# ==================== SETTINGS ====================

@login_required
def settings_view(request):
    """Comprehensive settings page"""
    user = request.user
    
    if request.method == 'POST':
        section = request.POST.get('section')
        
        if section == 'account':
            # Update account information
            user.fullname = request.POST.get('fullname', user.fullname)
            user.email = request.POST.get('email', user.email)
            user.phone = request.POST.get('phone', user.phone)
            user.bio = request.POST.get('bio', user.bio)
            
            # Handle password change
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            if current_password and new_password:
                if user.check_password(current_password):
                    if new_password == confirm_password:
                        user.set_password(new_password)
                        messages.success(request, 'Password updated successfully!')
                    else:
                        messages.error(request, 'New passwords do not match.')
                        return redirect('settings')
                else:
                    messages.error(request, 'Current password is incorrect.')
                    return redirect('settings')
            
            user.save()
            messages.success(request, 'Account settings updated successfully!')
        
        elif section == 'notifications':
            # Save notification preferences (you can extend User model or create UserSettings model)
            messages.success(request, 'Notification preferences saved!')
        
        elif section == 'privacy':
            # Save privacy settings
            messages.success(request, 'Privacy settings saved!')
        
        elif section == 'payments':
            # Save payment information
            gcash_number = request.POST.get('gcash_number')
            # Store in user profile or separate payment settings
            messages.success(request, 'Payment settings saved!')
        
        elif section == 'preferences':
            # Save task preferences
            messages.success(request, 'Preferences saved!')
        
        return redirect('settings')
    
    return render(request, 'settings.html', {
        'user': user,
    })


# ==================== MESSAGES ====================

@login_required
def messages_list(request, task_id=None):
    """Messenger-style interface with conversations list and active chat"""
    user = request.user
    
    # Handle delete conversation
    if request.method == 'POST' and 'delete_task_id' in request.POST:
        task_id = request.POST.get('delete_task_id')
        try:
            task = Task.objects.get(id=task_id)
            # Check if user is part of this conversation
            if task.poster == user or task.doer == user:
                # Delete all messages for this task
                Message.objects.filter(task=task).delete()
                messages.success(request, 'Conversation deleted successfully')
            else:
                messages.error(request, 'You do not have permission to delete this conversation')
        except Task.DoesNotExist:
            messages.error(request, 'Task not found')
        return redirect('messages_list')
    
    # Handle send message
    if request.method == 'POST' and 'message_content' in request.POST and task_id:
        try:
            task = Task.objects.get(id=task_id)
            if user in [task.poster, task.doer]:
                # Check chat access (5-message limit)
                chat_access = check_chat_access(task_id, user)
                if chat_access['allowed']:
                    message_content = request.POST.get('message_content', '').strip()
                    if message_content:
                        message = Message.objects.create(
                            task=task,
                            sender=user,
                            message=message_content
                        )
                        
                        # Create notification for the other party
                        recipient = task.doer if task.poster == user else task.poster
                        if recipient:
                            Notification.objects.create(
                                user=recipient,
                                type='system_message',
                                title=f'New message in "{task.title}"',
                                message=f'{user.fullname} sent you a message.',
                                related_task=task
                            )
                        
                        # Show warning if approaching limit
                        if chat_access.get('free_tier') and chat_access.get('messages_remaining', 0) <= 2:
                            remaining = chat_access['messages_remaining'] - 1
                            if remaining > 0:
                                messages.warning(request, f"⚠️ {remaining} free message(s) remaining. Pay ₱2 to unlock unlimited chat.")
                            else:
                                messages.warning(request, "⚠️ This was your last free message. Pay ₱2 to continue chatting.")
                else:
                    messages.error(request, chat_access['reason'])
        except Task.DoesNotExist:
            pass
        return redirect('messages_chat', task_id=task_id)
    
    # Get all tasks where user has chat access
    if user.role == 'task_doer':
        tasks_with_chat = Task.objects.filter(
            doer=user
        ).exclude(
            status='open'
        ).select_related('poster').order_by('-updated_at')
    elif user.role == 'task_poster':
        tasks_with_chat = Task.objects.filter(
            poster=user
        ).exclude(
            doer__isnull=True
        ).select_related('doer').order_by('-updated_at')
    else:
        tasks_with_chat = Task.objects.exclude(
            doer__isnull=True
        ).select_related('poster', 'doer').order_by('-updated_at')
    
    # Get last message and unread count for each task
    conversations = []
    for task in tasks_with_chat:
        last_message = Message.objects.filter(task=task).order_by('-created_at').first()
        unread_count = Message.objects.filter(
            task=task,
            is_read=False
        ).exclude(sender=user).count()
        
        if user == task.poster:
            other_user = task.doer
        else:
            other_user = task.poster
        
        payment_pending = False
        payment_completed = False
        
        if task.status == 'completed' and user == task.poster:
            try:
                payment = Payment.objects.get(task=task)
                if payment.status == 'pending_payment' or payment.status == 'pending_confirmation':
                    payment_pending = True
                elif payment.status == 'confirmed':
                    payment_completed = True
            except Payment.DoesNotExist:
                payment_pending = True
        
        conversations.append({
            'task': task,
            'other_user': other_user,
            'last_message': last_message,
            'unread_count': unread_count,
            'payment_pending': payment_pending,
            'payment_completed': payment_completed,
        })
    
    # Get active chat data if task_id provided
    active_task = None
    active_messages = []
    other_user = None
    chat_access = None
    
    if task_id:
        try:
            active_task = Task.objects.get(id=task_id)
            if user in [active_task.poster, active_task.doer]:
                # Get all messages for this task
                active_messages = Message.objects.filter(task=active_task).order_by('created_at')
                # Mark messages as read
                Message.objects.filter(task=active_task).exclude(sender=user).update(is_read=True)
                # Get other user
                other_user = active_task.doer if user == active_task.poster else active_task.poster
                # Check chat access
                chat_access = check_chat_access(task_id, user)
        except Task.DoesNotExist:
            pass
    elif conversations:
        # Auto-select first conversation
        active_task = conversations[0]['task']
        active_messages = Message.objects.filter(task=active_task).order_by('created_at')
        Message.objects.filter(task=active_task).exclude(sender=user).update(is_read=True)
        other_user = conversations[0]['other_user']
        chat_access = check_chat_access(active_task.id, user)
    
    context = {
        'conversations': conversations,
        'active_task': active_task,
        'active_messages': active_messages,
        'other_user': other_user,
        'chat_access': chat_access,
        'message_form': MessageForm(),
    }
    
    return render(request, 'messages/list.html', context)


@login_required
def chat_view(request, task_id):
    """Facebook Messenger-style chat interface for a specific task"""
    task = get_object_or_404(Task, id=task_id)
    user = request.user
    
    # Check if user can access this chat
    if user not in [task.poster, task.doer]:
        messages.error(request, "You don't have permission to access this chat.")
        return redirect('messages_list')
    
    # Check chat access (5-message limit)
    chat_access = check_chat_access(task_id, user)
    
    # Get all messages for this task
    task_messages = Message.objects.filter(task=task).order_by('created_at')
    
    # Mark messages as read
    Message.objects.filter(task=task).exclude(sender=user).update(is_read=True)
    
    # Get all conversations for sidebar
    if user.role == 'task_doer':
        all_tasks = Task.objects.filter(doer=user).exclude(status='open').select_related('poster').order_by('-updated_at')
    elif user.role == 'task_poster':
        all_tasks = Task.objects.filter(poster=user).exclude(doer__isnull=True).select_related('doer').order_by('-updated_at')
    else:
        all_tasks = Task.objects.exclude(doer__isnull=True).select_related('poster', 'doer').order_by('-updated_at')
    
    # Determine the other user
    other_user = task.doer if user == task.poster else task.poster
    
    # Get message count for limit tracking
    message_count = task_messages.count()
    
    context = {
        'task': task,
        'messages': task_messages,
        'message_count': message_count,
        'chat_access': chat_access,
        'other_user': other_user,
        'all_tasks': all_tasks,
        'message_form': MessageForm(),
    }
    
    return render(request, 'chat_modern.html', context)


@login_required
def payments_dashboard(request):
    """Comprehensive payments dashboard with statistics and history"""
    user = request.user
    from django.db.models import Sum, Count, Q
    from datetime import datetime, timedelta
    
    # Get all payments for the user
    if user.role == 'task_doer':
        # Doer sees payments they receive
        all_payments = Payment.objects.filter(
            task__doer=user
        ).select_related('task', 'task__poster', 'task__doer').order_by('-created_at')
    elif user.role == 'task_poster':
        # Poster sees payments they make
        all_payments = Payment.objects.filter(
            task__poster=user
        ).select_related('task', 'task__poster', 'task__doer').order_by('-created_at')
    else:
        # Admin sees all payments
        all_payments = Payment.objects.all().select_related(
            'task', 'task__poster', 'task__doer'
        ).order_by('-created_at')
    
    # Calculate statistics
    total_payments = all_payments.aggregate(
        total=Sum('amount'),
        count=Count('id')
    )
    
    confirmed_payments = all_payments.filter(status='confirmed').aggregate(
        total=Sum('amount'),
        count=Count('id')
    )
    
    pending_payments_agg = all_payments.filter(
        Q(status='pending_payment') | Q(status='pending_confirmation')
    ).aggregate(
        total=Sum('amount'),
        count=Count('id')
    )
    
    # This month's payments
    first_day_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_payments = all_payments.filter(
        created_at__gte=first_day_of_month,
        status='confirmed'
    ).aggregate(
        total=Sum('amount'),
        count=Count('id')
    )
    
    # Calculate success rate
    total_count = total_payments['count'] or 0
    completed_count = confirmed_payments['count'] or 0
    success_rate = (completed_count / total_count * 100) if total_count > 0 else 0
    
    stats = {
        'total_amount': confirmed_payments['total'] or 0,
        'pending_amount': pending_payments_agg['total'] or 0,
        'pending_count': pending_payments_agg['count'] or 0,
        'month_amount': month_payments['total'] or 0,
        'month_count': month_payments['count'] or 0,
        'success_rate': success_rate,
        'total_count': total_count,
        'completed_count': completed_count,
    }
    
    # Get pending payments (tasks completed but not paid)
    if user.role == 'task_poster':
        pending_tasks = Task.objects.filter(
            poster=user,
            status='completed'
        ).select_related('doer')
        
        pending_payments_list = []
        for task in pending_tasks:
            try:
                payment = Payment.objects.get(task=task)
                if payment.status in ['pending_payment', 'pending_confirmation']:
                    pending_payments_list.append({
                        'task': task,
                        'payment': payment,
                        'other_user': task.doer
                    })
            except Payment.DoesNotExist:
                pending_payments_list.append({
                    'task': task,
                    'payment': None,
                    'other_user': task.doer
                })
    elif user.role == 'task_doer':
        pending_tasks = Task.objects.filter(
            doer=user,
            status='completed'
        ).select_related('poster')
        
        pending_payments_list = []
        for task in pending_tasks:
            try:
                payment = Payment.objects.get(task=task)
                if payment.status in ['pending_payment', 'pending_confirmation']:
                    pending_payments_list.append({
                        'task': task,
                        'payment': payment,
                        'other_user': task.poster
                    })
            except Payment.DoesNotExist:
                pending_payments_list.append({
                    'task': task,
                    'payment': None,
                    'other_user': task.poster
                })
    else:
        pending_payments_list = []
    
    # Get payment history (limit to 50 most recent)
    payment_history = all_payments[:50]
    
    context = {
        'stats': stats,
        'pending_payments': pending_payments_list,
        'payment_history': payment_history,
    }
    
    return render(request, 'payments.html', context)
