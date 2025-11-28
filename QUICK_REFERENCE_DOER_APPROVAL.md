# ⚡ Quick Reference: Doer Approval Workflow

## What Changed?

### Before ❌
- Doers could directly accept tasks
- No waiting period
- No poster approval needed
- Doers could apply multiple times

### After ✅
- Doers must apply through application system
- Must wait for poster approval
- Poster reviews and chooses best applicant
- Prevents duplicate applications

---

## For Task Doers

### Workflow
```
1. Browse tasks
2. Click "Apply for Task"
3. Submit application with cover letter
4. See "Waiting for Review" status (YELLOW)
5. Wait for poster decision
6. If accepted → "Application Accepted! ✅" (GREEN)
7. If rejected → "Application Rejected" (RED)
8. Can apply again if rejected
```

### Status Indicators
- 🟡 **Yellow (Waiting for Review)**: Application pending
- 🟢 **Green (Accepted)**: You're chosen! Start working
- 🔴 **Red (Rejected)**: Can apply again
- 🔵 **Blue (Apply)**: No application yet

### What You Can Do
- ✅ Apply for tasks
- ✅ Wait for poster decision
- ✅ Apply again if rejected
- ✅ Start work once accepted
- ❌ Cannot start work without acceptance
- ❌ Cannot apply multiple times

---

## For Task Posters

### Workflow
```
1. Post a task
2. Doers apply for task
3. Click "View Applications" button
4. See ranked list of applicants
5. Review each applicant:
   - Rating
   - Completed tasks
   - Validated skills
   - Recent feedback
6. Click "Accept" for chosen doer
7. All other applications auto-rejected
8. Chosen doer notified and can start work
```

### What You See
- **Pending Applications**: Ranked by score (best first)
- **Accepted Applications**: Green section showing chosen doer
- **Rejected Applications**: Collapsed section (can expand)

### What You Can Do
- ✅ View all applications
- ✅ See applicant rankings
- ✅ Accept best applicant
- ✅ Reject applicants
- ✅ See applicant ratings and skills
- ❌ Cannot directly assign without application

---

## Database Status Values

### TaskApplication.status
```
'pending'  → Waiting for poster review
'accepted' → Poster chose this doer
'rejected' → Poster rejected this doer
```

### Task.status
```
'open'        → Accepting applications
'in_progress' → Doer chosen, working
'completed'   → Work finished
'cancelled'   → Task cancelled
```

---

## Key URLs

| Page | URL | Who |
|------|-----|-----|
| Apply for Task | `/tasks/<task_id>/apply/` | Doer |
| View Applications | `/tasks/<task_id>/applications/` | Poster |
| Accept Application | `/application/<app_id>/accept/` | Poster |
| Reject Application | `/application/<app_id>/reject/` | Poster |
| Task Detail | `/tasks/<task_id>/` | Both |

---

## Visual Indicators

### Doer View - Pending
```
┌─────────────────────────────────┐
│ ⏱️  Waiting for Review          │
│                                 │
│ Your application is pending.    │
│ The task poster is reviewing    │
│ applicants.                     │
└─────────────────────────────────┘
```

### Doer View - Accepted
```
┌─────────────────────────────────┐
│ ✅ Application Accepted!        │
│                                 │
│ You've been chosen! You can     │
│ now start working on this task. │
└─────────────────────────────────┘
```

### Doer View - Rejected
```
┌─────────────────────────────────┐
│ ❌ Application Rejected         │
│                                 │
│ [Apply Again Button]            │
└─────────────────────────────────┘
```

---

## Testing Checklist

### As Task Doer
- [ ] Browse tasks
- [ ] Click "Apply for Task"
- [ ] Submit application
- [ ] See "Waiting for Review" (YELLOW)
- [ ] Try to apply again - blocked
- [ ] Wait for poster decision
- [ ] See "Application Accepted! ✅" (GREEN)
- [ ] Click "Open Chat" - works
- [ ] Click "Submit Work" - works

### As Task Poster
- [ ] Post task
- [ ] See "View Applications" button
- [ ] Click button
- [ ] See ranked applicants
- [ ] Click "Accept Application"
- [ ] Confirm task status → "in_progress"
- [ ] Verify task hidden from browse list
- [ ] Verify doer got notification

---

## Common Issues & Solutions

### Issue: "Apply for Task" button not showing
**Solution**: 
- Check if task status is "open"
- Check if you already applied
- Check if you're the task poster

### Issue: "Waiting for Review" but can't see status
**Solution**:
- Refresh the page
- Check if application was created
- Check database: `TaskApplication` table

### Issue: "Application Accepted" but can't work
**Solution**:
- Check if task status is "in_progress"
- Check if you're assigned as doer
- Try refreshing page

### Issue: Can't see "View Applications" button
**Solution**:
- Check if you're the task poster
- Check if task status is "open"
- Check if you're logged in

---

## Performance Notes

✅ **Optimized Queries**
- Uses `select_related` for poster/doer
- Uses `prefetch_related` for ratings/skills
- Indexed on status, poster, doer fields

✅ **Fast Status Checks**
- Application status cached in context
- No N+1 queries
- Single database lookup per page

---

## Summary

The doer approval workflow ensures:
1. **Fair Selection**: Posters choose best applicant
2. **Clear Communication**: Doers know their status
3. **No Premature Work**: Doers wait for approval
4. **Transparent Process**: Applicants ranked by score
5. **Easy Management**: One-click accept/reject

Everything is working correctly! 🎉
