# ErrandExpress - Complete Testing Guide

## Overview
This guide provides step-by-step instructions to test all 4 objectives and verify they are properly implemented and aligned.

---

## OBJECTIVE NO.1: Task Assignment System

### 1.1 Test Automatic Task Assignment
**Location**: `/api/auto-assign/<task_id>/`

**Steps**:
1. Create a task as faculty (task_poster)
2. Open browser DevTools → Network tab
3. Call API: `POST /api/auto-assign/<task_id>/`
4. Verify response:
   ```json
   {
     "success": true,
     "assignment_id": "uuid",
     "assigned_to": "Student Name",
     "score": 85.5
   }
   ```
5. Check database: `TaskAssignment` record created
6. Verify notification sent to student

**Expected Result**: ✅ Task automatically assigned to best-matching student

---

### 1.2 Test Manual Task Assignment
**Location**: `/api/manual-assign/<task_id>/`

**Steps**:
1. Create a task as faculty
2. Call API: `POST /api/manual-assign/<task_id>/`
   ```json
   {
     "agent_id": "student_uuid"
   }
   ```
3. Verify response: `{"success": true}`
4. Check database: `TaskAssignment` created
5. Verify notification sent

**Expected Result**: ✅ Task assigned to selected student

---

### 1.3 Test Task Reassignment
**Location**: `/api/reassign/<assignment_id>/`

**Steps**:
1. Get existing assignment ID
2. Call API: `POST /api/reassign/<assignment_id>/`
   ```json
   {
     "new_agent_id": "different_student_uuid"
   }
   ```
3. Verify old assignment status changed
4. Verify new assignment created
5. Check notifications sent to both students

**Expected Result**: ✅ Task reassigned with proper notifications

---

### 1.4 Test Assignment Notifications
**Location**: Notifications page

**Steps**:
1. Perform auto-assign
2. Go to `/notifications/`
3. Verify notification appears:
   - Type: "task_assigned"
   - Message: "You have been assigned to [Task Name]"
   - Related task link works

**Expected Result**: ✅ Notifications display correctly

---

## OBJECTIVE NO.2: Payment System (PayMongo Integration)

### 2.1 Test Receipt Generation & Download
**Location**: `/api/download-receipt/<payment_id>/`

**Steps**:
1. Create a completed payment
2. Call API: `GET /api/download-receipt/<payment_id>/`
3. Verify file downloads as `.txt`
4. Check receipt contains:
   - Receipt number (payment ID)
   - Transaction date
   - Task details
   - Amount and commission breakdown
   - Payer/receiver names
   - Status

**Expected Result**: ✅ Receipt downloads with all details

---

### 2.2 Test Payment Details API
**Location**: `/api/payment-details/<payment_id>/`

**Steps**:
1. Create a payment record
2. Call API: `GET /api/payment-details/<payment_id>/`
3. Verify response:
   ```json
   {
     "success": true,
     "payment": {
       "id": "uuid",
       "task_title": "Task Name",
       "amount": "100.00",
       "commission_amount": "10.00",
       "net_amount": "90.00",
       "status": "confirmed"
     }
   }
   ```

**Expected Result**: ✅ Payment details returned correctly

---

### 2.3 Test 10% Commission Calculation
**Location**: Database → Payment model

**Steps**:
1. Create payment with amount ₱500
2. Check database:
   - `amount` = 500.00
   - `commission_amount` = 50.00 (10%)
   - `net_amount` = 450.00
3. Test with different amounts (₱100, ₱1000, ₱250)
4. Verify calculation: `commission = amount × 0.10`

**Expected Result**: ✅ Commission calculated correctly for all amounts

---

### 2.4 Test Duplicate Payment Prevention
**Location**: Database constraints

**Steps**:
1. Create payment: Task A, Payer X, Receiver Y
2. Try to create duplicate with same task/payer/receiver
3. Verify IntegrityError raised
4. Check `paymongo_payment_id` unique constraint
5. Try duplicate PayMongo ID
6. Verify error

**Expected Result**: ✅ Duplicates prevented by database constraints

---

### 2.5 Test Payment Reconciliation
**Location**: Celery task `reconcile_pending_payments`

**Steps**:
1. Create payment with status "pending"
2. Set `created_at` to 1+ hour ago
3. Run: `python manage.py celery -A errandexpress worker`
4. Wait for reconciliation task (every 30 min)
5. Or manually call: `from core.tasks import reconcile_pending_payments; reconcile_pending_payments.delay()`
6. Check payment status updated to "confirmed"

**Expected Result**: ✅ Pending payments reconciled automatically

---

### 2.6 Test Payment UI Integration
**Location**: `/payments/`

**Steps**:
1. Navigate to `/payments/`
2. View payment history table
3. Click "View" button on any payment
4. Verify modal shows:
   - Gross amount
   - Commission (10%)
   - Net amount
5. Click "Receipt" button
6. Verify file downloads

**Expected Result**: ✅ UI displays commission breakdown and receipt works

---

## OBJECTIVE NO.3: Task Monitoring & Feedback System

### 3.1 Test Monitoring Dashboard Access
**Location**: `/monitoring/`

**Steps**:
1. Login as faculty
2. Navigate to `/monitoring/`
3. Verify dashboard shows:
   - Total tasks count
   - Completed tasks count
   - In-progress tasks count
   - Completion rate %
4. Verify table displays all posted tasks
5. Login as student
6. Navigate to `/monitoring/`
7. Verify table shows assigned tasks (not posted)

**Expected Result**: ✅ Role-specific monitoring dashboards work

---

### 3.2 Test Feedback Submission
**Location**: `/api/submit-feedback/<task_id>/`

**Steps**:
1. Complete a task
2. Call API: `POST /api/submit-feedback/<task_id>/`
   ```json
   {
     "score": 9,
     "feedback": "Great work!"
   }
   ```
3. Verify response: `{"success": true}`
4. Check database: `Rating` record created
5. Verify fields:
   - `score` = 9
   - `feedback` = "Great work!"
   - `rater` = current user
   - `rated` = other party

**Expected Result**: ✅ Feedback saved correctly

---

### 3.3 Test Feedback Validation
**Location**: `/api/submit-feedback/<task_id>/`

**Steps**:
1. Try score = 0 (invalid)
   - Verify error: "Score must be between 1 and 10"
2. Try score = 15 (invalid)
   - Verify error: "Score must be between 1 and 10"
3. Try on non-completed task
   - Verify error: "Task must be completed"
4. Try unauthorized user
   - Verify error: "Unauthorized"

**Expected Result**: ✅ All validations work correctly

---

### 3.4 Test Feedback Retrieval
**Location**: `/api/get-feedback/<task_id>/`

**Steps**:
1. Create multiple ratings for a task
2. Call API: `GET /api/get-feedback/<task_id>/`
3. Verify response includes all ratings:
   ```json
   {
     "success": true,
     "feedback": [
       {
         "rater_name": "John",
         "rated_name": "Jane",
         "score": 9,
         "feedback": "Great!"
       }
     ],
     "count": 1
   }
   ```

**Expected Result**: ✅ All feedback retrieved correctly

---

### 3.5 Test Feedback Notifications
**Location**: Notifications page

**Steps**:
1. Submit feedback for a task
2. Check notifications for rated user
3. Verify notification:
   - Type: "rating_received"
   - Title: "⭐ You received a 9/10 rating"
   - Message includes task name
   - Related task link works

**Expected Result**: ✅ Notifications sent and displayed

---

### 3.6 Test Monitoring UI
**Location**: `/monitoring/`

**Steps**:
1. Navigate to monitoring dashboard
2. Verify statistics cards display correctly
3. Verify task table shows all tasks
4. For completed tasks, verify "Rate" button appears
5. Click "Rate" button
6. Verify feedback modal opens
7. Select rating 1-10
8. Add optional feedback
9. Click "Submit"
10. Verify success message
11. Verify page reloads

**Expected Result**: ✅ UI works end-to-end

---

## OBJECTIVE NO.4: System Integration & Alignment

### 4.1 Test End-to-End Task Flow
**Steps**:
1. **Faculty posts task** → `/tasks/create/`
   - Verify task created
   - Verify SystemCommission created
2. **Auto-assign task** → `/api/auto-assign/<task_id>/`
   - Verify student assigned
   - Verify notification sent
3. **Student accepts task** → Task detail page
   - Verify status changes to "in_progress"
4. **Chat messaging** → `/messages/`
   - Send 5 messages (free tier)
   - Try 6th message (should be blocked)
   - Pay ₱2 system fee
   - Verify chat unlocked
5. **Complete task** → Task detail page
   - Mark as complete
   - Verify payment created
6. **Rate and feedback** → `/monitoring/`
   - Submit rating
   - Verify feedback saved
7. **View payment history** → `/payments/`
   - Verify payment displayed
   - Download receipt
   - Check commission breakdown

**Expected Result**: ✅ Complete workflow functions correctly

---

### 4.2 Test Database Integrity
**Steps**:
1. Open Django shell: `python manage.py shell`
2. Run tests:
   ```python
   from core.models import Task, Payment, Rating, TaskAssignment, Notification
   
   # Check relationships
   task = Task.objects.first()
   print(f"Task assignments: {task.taskassignment_set.count()}")
   print(f"Payments: {task.payment}")
   print(f"Ratings: {Rating.objects.filter(task=task).count()}")
   
   # Check commission calculation
   payment = Payment.objects.first()
   assert payment.commission_amount == payment.amount * 0.10
   assert payment.net_amount == payment.amount - payment.commission_amount
   
   # Check unique constraints
   print("Database integrity: OK")
   ```

**Expected Result**: ✅ All relationships and constraints verified

---

### 4.3 Test API Endpoints
**Steps**:
1. Run all API tests:
   ```bash
   python manage.py test core.tests.MonitoringTests
   python manage.py test core.tests.PaymentTests
   ```
2. Verify all tests pass
3. Check coverage:
   ```bash
   coverage run --source='core' manage.py test
   coverage report
   ```

**Expected Result**: ✅ All tests pass with good coverage

---

### 4.4 Test Navigation & Sidebar
**Steps**:
1. Login as faculty
2. Check sidebar has:
   - Dashboard
   - Post Task
   - Notifications
   - My Tasks
   - Messages
   - Payments
   - **Monitoring** ← NEW
   - Validate Skills
   - Profile
3. Click each link
4. Verify pages load correctly
5. Login as student
6. Verify sidebar shows:
   - Dashboard
   - Browse Tasks (instead of Post Task)
   - Notifications
   - My Tasks
   - Messages
   - Payments
   - **Monitoring** ← NEW
   - Validate Skills
   - Profile

**Expected Result**: ✅ Navigation complete and role-specific

---

### 4.5 Test Performance
**Steps**:
1. Open DevTools → Performance tab
2. Navigate to `/monitoring/`
3. Check metrics:
   - First Contentful Paint < 2s
   - Largest Contentful Paint < 3s
   - Cumulative Layout Shift < 0.1
4. Navigate to `/payments/`
5. Check same metrics
6. Load task with 100+ messages
7. Verify chat loads smoothly

**Expected Result**: ✅ Performance meets standards

---

### 4.6 Test Security
**Steps**:
1. Try accessing `/monitoring/` without login
   - Should redirect to login
2. Try accessing other user's payment details
   - Should return 403 Unauthorized
3. Try accessing other user's feedback
   - Should return 403 Unauthorized
4. Try submitting feedback for non-assigned task
   - Should return 403 Unauthorized
5. Check CSRF tokens on forms
6. Verify no sensitive data in logs

**Expected Result**: ✅ All security checks pass

---

## Quick Test Checklist

### Objective 1: Task Assignment
- [ ] Auto-assign works
- [ ] Manual assign works
- [ ] Reassignment works
- [ ] Notifications sent
- [ ] Database records created

### Objective 2: Payment System
- [ ] Receipt downloads
- [ ] Payment details API works
- [ ] Commission calculated (10%)
- [ ] Duplicates prevented
- [ ] Reconciliation works
- [ ] UI shows commission breakdown

### Objective 3: Monitoring & Feedback
- [ ] Dashboard accessible
- [ ] Statistics display correctly
- [ ] Feedback submission works
- [ ] Validation works
- [ ] Notifications sent
- [ ] UI functional

### Objective 4: Integration
- [ ] End-to-end flow works
- [ ] Database integrity verified
- [ ] All tests pass
- [ ] Navigation complete
- [ ] Performance good
- [ ] Security verified

---

## Running All Tests

```bash
# Run all tests
python manage.py test core

# Run specific test class
python manage.py test core.tests.PaymentTests
python manage.py test core.tests.MonitoringTests

# Run with coverage
coverage run --source='core' manage.py test
coverage report
coverage html  # Generate HTML report

# Run with verbosity
python manage.py test core -v 2

# Run specific test method
python manage.py test core.tests.PaymentTests.test_create_payment
```

---

## Manual Testing Workflow

### Day 1: Objective 1 & 2
1. Create task as faculty
2. Auto-assign to student
3. Verify assignment notification
4. Complete task
5. Download receipt
6. Verify commission breakdown

### Day 2: Objective 3 & 4
1. Navigate to monitoring
2. View task statistics
3. Submit feedback
4. Verify notification
5. Check payment history
6. Test end-to-end flow

### Day 3: Integration & Performance
1. Test all navigation links
2. Run performance tests
3. Test security (unauthorized access)
4. Run full test suite
5. Check database integrity

---

## Success Criteria

✅ **All objectives implemented**: 4/4
✅ **All tests passing**: 100%
✅ **No security issues**: Verified
✅ **Performance acceptable**: < 3s load time
✅ **UI consistent**: Matches system design
✅ **Database integrity**: All constraints working
✅ **Notifications working**: All types sent
✅ **APIs functional**: All endpoints tested

---

## Troubleshooting

### Payment API returns 403
- Check user is payer or receiver
- Verify payment exists
- Check authorization logic

### Feedback not saving
- Verify task is completed
- Check user is poster or doer
- Verify score is 1-10
- Check CSRF token

### Monitoring page blank
- Verify user is logged in
- Check user has tasks
- Verify role is set correctly
- Check database has data

### Commission not calculated
- Verify payment.save() called
- Check model save() method
- Verify decimal precision
- Test with different amounts

---

## Contact & Support

For issues or questions about testing:
1. Check Django logs: `tail -f logs/django.log`
2. Check Celery logs: `tail -f logs/celery.log`
3. Run Django shell for debugging
4. Check database directly with psql/pgAdmin

