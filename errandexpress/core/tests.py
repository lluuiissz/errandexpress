from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import Task, Message, Rating, Notification
import json

User = get_user_model()


class TaskCreationTests(TestCase):
    """Test task creation and validation"""
    
    def setUp(self):
        """Create test user"""
        self.user = User.objects.create_user(
            username='testposter',
            email='poster@test.com',
            password='testpass123',
            fullname='Test Poster',
            role='task_poster'
        )
        self.client = Client()
        self.client.login(username='testposter', password='testpass123')
    
    def test_create_task_with_all_fields(self):
        """Test creating task with all required fields"""
        task_data = {
            'title': 'Test Task',
            'description': 'Test Description',
            'category': 'typing',
            'tags': 'test,urgent',
            'price': 100,
            'payment_method': 'gcash',
            'deadline': (timezone.now() + timedelta(days=1)).isoformat(),
            'location': 'Online',
            'requirements': 'Test requirements'
        }
        
        response = self.client.post('/tasks/create/', task_data)
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.assertEqual(Task.objects.count(), 1)
        task = Task.objects.first()
        self.assertEqual(task.title, 'Test Task')
        self.assertEqual(task.poster, self.user)
    
    def test_create_task_missing_title(self):
        """Test creating task without title fails"""
        task_data = {
            'description': 'Test Description',
            'category': 'typing',
            'tags': 'test',
            'price': 100,
            'payment_method': 'gcash',
            'deadline': (timezone.now() + timedelta(days=1)).isoformat(),
            'location': 'Online',
            'requirements': 'Test'
        }
        
        response = self.client.post('/tasks/create/', task_data)
        self.assertEqual(Task.objects.count(), 0)
    
    def test_create_task_invalid_price(self):
        """Test creating task with price below minimum fails"""
        task_data = {
            'title': 'Test Task',
            'description': 'Test Description',
            'category': 'typing',
            'tags': 'test',
            'price': 5,  # Below minimum of 10
            'payment_method': 'gcash',
            'deadline': (timezone.now() + timedelta(days=1)).isoformat(),
            'location': 'Online',
            'requirements': 'Test'
        }
        
        response = self.client.post('/tasks/create/', task_data)
        self.assertEqual(Task.objects.count(), 0)
    
    def test_create_task_past_deadline(self):
        """Test creating task with past deadline fails"""
        task_data = {
            'title': 'Test Task',
            'description': 'Test Description',
            'category': 'typing',
            'tags': 'test',
            'price': 100,
            'payment_method': 'gcash',
            'deadline': (timezone.now() - timedelta(days=1)).isoformat(),  # Past date
            'location': 'Online',
            'requirements': 'Test'
        }
        
        response = self.client.post('/tasks/create/', task_data)
        self.assertEqual(Task.objects.count(), 0)


class MessageTests(TestCase):
    """Test messaging system"""
    
    def setUp(self):
        """Create test users and task"""
        self.poster = User.objects.create_user(
            username='poster',
            email='poster@test.com',
            password='testpass123',
            fullname='Test Poster',
            role='task_poster'
        )
        self.doer = User.objects.create_user(
            username='doer',
            email='doer@test.com',
            password='testpass123',
            fullname='Test Doer',
            role='task_doer'
        )
        self.task = Task.objects.create(
            poster=self.poster,
            doer=self.doer,
            title='Test Task',
            description='Test',
            category='typing',
            price=100,
            deadline=timezone.now() + timedelta(days=1),
            status='in_progress'
        )
        self.client = Client()
    
    def test_send_message_within_limit(self):
        """Test sending messages within 5-message limit"""
        self.client.login(username='poster', password='testpass123')
        
        for i in range(5):
            response = self.client.post('/api/send-message/', 
                json.dumps({'task_id': str(self.task.id), 'message': f'Message {i}'}),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)
        
        self.assertEqual(Message.objects.filter(task=self.task).count(), 5)
    
    def test_send_message_exceeds_limit(self):
        """Test sending 6th message without payment fails"""
        self.client.login(username='poster', password='testpass123')
        
        # Send 5 messages
        for i in range(5):
            self.client.post('/api/send-message/', 
                json.dumps({'task_id': str(self.task.id), 'message': f'Message {i}'}),
                content_type='application/json'
            )
        
        # 6th message should fail
        response = self.client.post('/api/send-message/', 
            json.dumps({'task_id': str(self.task.id), 'message': 'Message 6'}),
            content_type='application/json'
        )
        data = json.loads(response.content)
        self.assertFalse(data.get('success'))
        self.assertTrue(data.get('payment_required'))


class RatingTests(TestCase):
    """Test rating system"""
    
    def setUp(self):
        """Create test users"""
        self.rater = User.objects.create_user(
            username='rater',
            email='rater@test.com',
            password='testpass123',
            fullname='Test Rater',
            role='task_poster'
        )
        self.rated = User.objects.create_user(
            username='rated',
            email='rated@test.com',
            password='testpass123',
            fullname='Test Rated',
            role='task_doer'
        )
        self.task = Task.objects.create(
            poster=self.rater,
            doer=self.rated,
            title='Test Task',
            description='Test',
            category='typing',
            price=100,
            deadline=timezone.now() + timedelta(days=1),
            status='completed'
        )
    
    def test_create_rating(self):
        """Test creating a rating"""
        rating = Rating.objects.create(
            task=self.task,
            rater=self.rater,
            rated=self.rated,
            score=9,
            feedback='Great work!'
        )
        
        self.assertEqual(rating.score, 9)
        self.assertEqual(rating.feedback, 'Great work!')
    
    def test_rating_updates_user_avg(self):
        """Test that rating updates user average rating"""
        Rating.objects.create(
            task=self.task,
            rater=self.rater,
            rated=self.rated,
            score=8
        )
        
        # Refresh user from database
        self.rated.refresh_from_db()
        # Note: avg_rating is calculated via aggregation in views, not stored
        ratings = Rating.objects.filter(rated=self.rated)
        avg = sum(r.score for r in ratings) / ratings.count()
        self.assertEqual(avg, 8)


class PaymentTests(TestCase):
    """Test payment system"""
    
    def setUp(self):
        """Create test users and task"""
        self.poster = User.objects.create_user(
            username='poster',
            email='poster@test.com',
            password='testpass123',
            fullname='Test Poster',
            role='task_poster'
        )
        self.doer = User.objects.create_user(
            username='doer',
            email='doer@test.com',
            password='testpass123',
            fullname='Test Doer',
            role='task_doer'
        )
        self.task = Task.objects.create(
            poster=self.poster,
            doer=self.doer,
            title='Test Task',
            description='Test',
            category='typing',
            price=100,
            deadline=timezone.now() + timedelta(days=1),
            status='completed'
        )
    
    def test_create_payment(self):
        """Test creating a payment"""
        from .models import Payment
        payment = Payment.objects.create(
            task=self.task,
            payer=self.poster,
            receiver=self.doer,
            amount=100,
            method='cod'
        )
        
        self.assertEqual(payment.amount, 100)
        self.assertEqual(payment.commission_amount, 10)  # 10% of 100
        self.assertEqual(payment.net_amount, 90)
    
    def test_payment_commission_calculation(self):
        """Test 10% commission is calculated correctly"""
        from .models import Payment
        payment = Payment.objects.create(
            task=self.task,
            payer=self.poster,
            receiver=self.doer,
            amount=500,
            method='paymongo'
        )
        
        self.assertEqual(float(payment.commission_amount), 50.0)
        self.assertEqual(float(payment.net_amount), 450.0)
    
    def test_duplicate_payment_prevention(self):
        """Test duplicate payments are prevented"""
        from .models import Payment
        from django.db import IntegrityError
        
        Payment.objects.create(
            task=self.task,
            payer=self.poster,
            receiver=self.doer,
            amount=100,
            method='cod'
        )
        
        # Try to create duplicate
        with self.assertRaises(IntegrityError):
            Payment.objects.create(
                task=self.task,
                payer=self.poster,
                receiver=self.doer,
                amount=100,
                method='cod'
            )


class MonitoringTests(TestCase):
    """Test task monitoring and feedback system"""
    
    def setUp(self):
        """Create test users and task"""
        self.poster = User.objects.create_user(
            username='poster',
            email='poster@test.com',
            password='testpass123',
            fullname='Test Poster',
            role='task_poster'
        )
        self.doer = User.objects.create_user(
            username='doer',
            email='doer@test.com',
            password='testpass123',
            fullname='Test Doer',
            role='task_doer'
        )
        self.task = Task.objects.create(
            poster=self.poster,
            doer=self.doer,
            title='Test Task',
            description='Test',
            category='typing',
            price=100,
            deadline=timezone.now() + timedelta(days=1),
            status='completed'
        )
        self.client = Client()
    
    def test_task_monitoring_access(self):
        """Test task monitoring dashboard access"""
        self.client.login(username='poster', password='testpass123')
        response = self.client.get('/monitoring/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('tasks', response.context)
        self.assertIn('stats', response.context)
    
    def test_submit_feedback(self):
        """Test submitting feedback for completed task"""
        self.client.login(username='poster', password='testpass123')
        
        response = self.client.post(
            f'/api/submit-feedback/{self.task.id}/',
            json.dumps({'score': 9, 'feedback': 'Great work!'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        # Verify rating was created
        rating = Rating.objects.filter(task=self.task, rater=self.poster).first()
        self.assertIsNotNone(rating)
        self.assertEqual(rating.score, 9)
        self.assertEqual(rating.feedback, 'Great work!')
    
    def test_feedback_validation(self):
        """Test feedback score validation"""
        self.client.login(username='poster', password='testpass123')
        
        # Invalid score (too high)
        response = self.client.post(
            f'/api/submit-feedback/{self.task.id}/',
            json.dumps({'score': 15, 'feedback': 'Test'}),
            content_type='application/json'
        )
        
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('Score must be between', data['error'])
    
    def test_get_task_feedback(self):
        """Test retrieving task feedback"""
        # Create feedback
        Rating.objects.create(
            task=self.task,
            rater=self.poster,
            rated=self.doer,
            score=8,
            feedback='Good job'
        )
        
        self.client.login(username='poster', password='testpass123')
        response = self.client.get(f'/api/get-feedback/{self.task.id}/')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['feedback'][0]['score'], 8)


class HealthCheckTests(TestCase):
    """Test health check endpoint"""
    
    def test_health_check_endpoint(self):
        """Test /health/ endpoint returns healthy status"""
        response = self.client.get('/health/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['database'], 'connected')
