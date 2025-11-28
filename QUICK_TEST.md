# ErrandExpress - Quick Test Reference

## 30-Second Verification

```bash
# 1. Run verification script
python verify_objectives.py

# 2. Run all tests
python manage.py test core

# 3. Start server
python manage.py runserver
```

**Expected**: All pass ✅

---

## 5-Minute Manual Test

### Test 1: Task Assignment (2 min)
1. Login as faculty
2. Create task: `/tasks/create/`
3. Auto-assign: Check task detail page
4. Verify student got notification

### Test 2: Payment System (1.5 min)
1. Go to `/payments/`
2. Click "View" on any payment
3. Verify commission breakdown shown
4. Click "Receipt" to download

### Test 3: Monitoring (1.5 min)
1. Go to `/monitoring/`
2. View task statistics
3. Click "Rate" on completed task
4. Submit feedback (score 8)

---

## API Quick Test

### Using curl or Postman

#### Test Payment Details
```bash
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/payment-details/PAYMENT_ID/
```

#### Test Feedback Submission
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"score": 9, "feedback": "Great!"}' \
  http://localhost:8000/api/submit-feedback/TASK_ID/
```

#### Test Receipt Download
```bash
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/download-receipt/PAYMENT_ID/ \
  > receipt.txt
```

---

## Database Quick Check

```bash
python manage.py shell

# Check Payment model
from core.models import Payment
p = Payment.objects.first()
print(f"Amount: {p.amount}")
print(f"Commission: {p.commission_amount}")
print(f"Net: {p.net_amount}")
assert p.commission_amount == p.amount * 0.10

# Check TaskAssignment model
from core.models import TaskAssignment
a = TaskAssignment.objects.first()
print(f"Score: {a.score}")
print(f"Method: {a.assignment_method}")

# Check Rating model
from core.models import Rating
r = Rating.objects.first()
print(f"Score: {r.score}")
print(f"Feedback: {r.feedback}")

print("✅ All models working!")
```

---

## Test Checklist

### Objective 1: Task Assignment
- [ ] Auto-assign works
- [ ] Manual assign works
- [ ] Reassignment works
- [ ] Notifications sent

### Objective 2: Payment System
- [ ] Commission calculated (10%)
- [ ] Receipt downloads
- [ ] Payment details show
- [ ] Duplicates prevented

### Objective 3: Monitoring & Feedback
- [ ] Dashboard loads
- [ ] Statistics display
- [ ] Feedback submits
- [ ] Notifications sent

### Objective 4: Integration
- [ ] All links work
- [ ] UI consistent
- [ ] Performance good
- [ ] Security verified

---

## Common Test Scenarios

### Scenario 1: Complete Task Workflow
```
1. Faculty creates task
2. System auto-assigns to student
3. Student accepts task
4. Both chat (5 messages free)
5. Pay ₱2 for unlimited chat
6. Complete task
7. Rate each other
8. View payment history
```

### Scenario 2: Payment Processing
```
1. Create payment: ₱500
2. Check commission: ₱50 (10%)
3. Check net: ₱450
4. Download receipt
5. View payment details
6. Verify all info correct
```

### Scenario 3: Feedback System
```
1. Go to monitoring
2. View task statistics
3. Click "Rate" on completed task
4. Select score 1-10
5. Add optional feedback
6. Submit
7. Check notification
8. Verify feedback saved
```

---

## Performance Check

```bash
# Open DevTools → Performance tab
# Navigate to /monitoring/
# Check metrics:
# - First Contentful Paint < 2s ✅
# - Largest Contentful Paint < 3s ✅
# - Cumulative Layout Shift < 0.1 ✅
```

---

## Security Check

```bash
# Try accessing without login
curl http://localhost:8000/monitoring/
# Expected: Redirect to login ✅

# Try accessing other user's data
curl -H "Authorization: Bearer WRONG_TOKEN" \
  http://localhost:8000/api/payment-details/ID/
# Expected: 403 Unauthorized ✅
```

---

## Files to Check

### Backend
- ✅ `core/views.py` - Views and APIs
- ✅ `core/models.py` - Models with fields
- ✅ `core/tasks.py` - Celery tasks
- ✅ `core/tests.py` - Test classes

### Frontend
- ✅ `core/templates/monitoring/task_monitoring.html` - Dashboard
- ✅ `core/templates/base_complete.html` - Sidebar link
- ✅ `core/static/js/payments-dashboard.js` - Commission display

### Configuration
- ✅ `errandexpress/urls.py` - Routes
- ✅ `errandexpress/celery.py` - Task schedule
- ✅ `errandexpress/settings.py` - Settings

---

## Test Results Template

```
Date: ___________
Tester: ___________

OBJECTIVE 1: Task Assignment
- Auto-assign: [ ] Pass [ ] Fail
- Manual assign: [ ] Pass [ ] Fail
- Reassignment: [ ] Pass [ ] Fail
- Notifications: [ ] Pass [ ] Fail

OBJECTIVE 2: Payment System
- Commission calc: [ ] Pass [ ] Fail
- Receipt download: [ ] Pass [ ] Fail
- Payment details: [ ] Pass [ ] Fail
- Duplicate prevention: [ ] Pass [ ] Fail

OBJECTIVE 3: Monitoring & Feedback
- Dashboard: [ ] Pass [ ] Fail
- Feedback submit: [ ] Pass [ ] Fail
- Feedback validation: [ ] Pass [ ] Fail
- Notifications: [ ] Pass [ ] Fail

OBJECTIVE 4: Integration
- End-to-end: [ ] Pass [ ] Fail
- UI consistency: [ ] Pass [ ] Fail
- Performance: [ ] Pass [ ] Fail
- Security: [ ] Pass [ ] Fail

Overall: [ ] PASS [ ] FAIL
Notes: _____________________
```

---

## Troubleshooting Quick Links

| Issue | Solution |
|-------|----------|
| Tests fail | Run `python manage.py test core -v 2` |
| Server won't start | Check `python manage.py check` |
| Payment API error | Verify PayMongo credentials |
| Feedback not saving | Check task is completed |
| Notifications not sent | Verify Celery running |
| UI looks broken | Clear browser cache |
| Database error | Run migrations: `python manage.py migrate` |

---

## Success Indicators

✅ All 4 objectives implemented
✅ All tests passing (15+)
✅ No errors in Django check
✅ Server runs without issues
✅ UI loads correctly
✅ APIs respond correctly
✅ Database queries work
✅ Notifications send
✅ Performance acceptable
✅ Security verified

**If all above are ✅, system is READY FOR PRODUCTION** 🚀

