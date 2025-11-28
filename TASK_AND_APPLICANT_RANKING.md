# Task & Applicant Ranking System - Complete Implementation

## 🎯 Overview

Implemented two ranking systems to improve task discovery and applicant selection:

1. **Task Ranking** - Tasks from higher-rated posters appear at the top
2. **Applicant Ranking** - Applicants ranked by rating, experience, and skills

## 📊 Task Ranking System

### How It Works

Tasks are ranked using a **priority score** that considers:

```
Priority Score = (Skill Match × 1.0) + (Poster Rating × 2.0) + (Urgency × 1.0)
```

**Factors:**
- **Skill Match** (1.0x) - Does task match user's validated skills?
- **Poster Rating** (2.0x) - What's the task poster's average rating?
- **Urgency** (1.0x) - Is the deadline within 24 hours?

### Implementation

**File**: `core/views.py` - `get_matched_tasks_for_user()` function (lines 216-312)

**Key Features:**
- ✅ Real-time poster ratings from Rating table
- ✅ Skill matching based on user's validated skills
- ✅ Urgency detection for deadline-driven tasks
- ✅ Sorted by priority score (highest first)
- ✅ Falls back to creation date if scores are equal

**Code:**
```python
# Calculate poster rating in real-time
poster_rating_subquery = Rating.objects.filter(
    rated=OuterRef('poster')
).values('rated').annotate(
    avg_rating=Avg('score')
).values('avg_rating')

# Annotate tasks with scores
tasks = tasks.annotate(
    skill_match_score=...,  # 3 if match, 0 if no match
    urgency_score=...,      # 1 if deadline < 24h, 0 otherwise
    poster_rating=Coalesce(Subquery(...), 0.0),
    priority_score=ExpressionWrapper(
        (F('skill_match_score') * 1.0) +
        (F('poster_rating') * 2.0) +
        (F('urgency_score') * 1.0),
        output_field=DecimalField()
    )
).order_by('-priority_score', '-created_at')
```

### Example Ranking

```
Task 1: Typing Task
  Poster Rating: 4.5/10
  Skill Match: ✅ (User has typing skill)
  Deadline: 2 days away
  Priority Score: (3 × 1.0) + (4.5 × 2.0) + (0 × 1.0) = 12.0
  Position: #1 ⭐

Task 2: Graphics Task
  Poster Rating: 3.0/10
  Skill Match: ❌ (User doesn't have graphics skill)
  Deadline: 1 day away
  Priority Score: (0 × 1.0) + (3.0 × 2.0) + (1 × 1.0) = 7.0
  Position: #2

Task 3: Typing Task
  Poster Rating: 2.0/10
  Skill Match: ✅ (User has typing skill)
  Deadline: 5 days away
  Priority Score: (3 × 1.0) + (2.0 × 2.0) + (0 × 1.0) = 7.0
  Position: #3
```

## 👥 Applicant Ranking System

### How It Works

Applicants are ranked using a **ranking score** that considers:

```
Ranking Score = (Rating × 10) + (Completed Tasks × 2) + (Newbie Bonus × 15)
```

**Factors:**
- **Rating** (×10) - What's the applicant's average rating?
- **Completed Tasks** (×2) - How many tasks have they completed?
- **Newbie Bonus** (×15) - Are they new (< 3 tasks)? Give them a fair chance!

### Implementation

**File**: `core/views.py` - `view_applications()` function (lines 2019-2113)

**Key Features:**
- ✅ Real-time doer ratings from Rating table
- ✅ Completed task count
- ✅ Newbie bonus to encourage new doers
- ✅ Sorted by ranking score (highest first)
- ✅ Shows validated skills for each applicant
- ✅ Shows recent feedback/ratings

**Code:**
```python
# For each application, calculate ranking score
for app in app_list:
    app.current_rating = app.doer_current_rating
    app.current_completed = app.doer_completed_count
    app.current_is_newbie = app.doer_completed_count < 3
    
    # Calculate ranking score
    app.calculated_ranking_score = (
        (float(app.current_rating) * 10) +      # Rating weight
        (app.current_completed * 2) +            # Experience weight
        (15 if app.current_is_newbie else 0)    # Newbie bonus
    )
    
    # Get validated skills
    app.validated_skills_display = [...]

# Sort by ranking score (highest first)
app_list.sort(key=lambda x: x.calculated_ranking_score, reverse=True)
```

### Example Ranking

```
Applicant 1: Juan Dela Cruz
  Rating: 4.8/10
  Completed Tasks: 12
  Is Newbie: ❌
  Ranking Score: (4.8 × 10) + (12 × 2) + 0 = 72.0
  Validated Skills: ⌨️ Typing, 📊 PowerPoint
  Position: #1 ⭐

Applicant 2: Maria Santos
  Rating: 3.5/10
  Completed Tasks: 2
  Is Newbie: ✅
  Ranking Score: (3.5 × 10) + (2 × 2) + 15 = 54.0
  Validated Skills: 🎨 Graphics Design
  Position: #2

Applicant 3: Pedro Reyes
  Rating: 0/10 (No ratings yet)
  Completed Tasks: 0
  Is Newbie: ✅
  Ranking Score: (0 × 10) + (0 × 2) + 15 = 15.0
  Validated Skills: None
  Position: #3
```

## 📋 Applicant Card Information

Each applicant card shows:

### Header Section
- **Avatar** - First letter of name
- **Name** - Full name
- **New Doer Badge** - If < 3 completed tasks
- **Applied Time** - "Applied X minutes ago"
- **Ranking Score** - Highlighted in yellow

### Stats Grid (3 columns)
- **Rating** - Average rating (e.g., "4.8/10" or "No ratings yet")
- **Completed** - Number of completed tasks
- **Bonus** - Newbie bonus points ("+15 pts" or "—")

### Application Details
- **Cover Letter** - Why they're a good fit
- **Timeline** - When they can complete the task
- **Validated Skills** - ✅ Verified skills with badges
- **Recent Feedback** - Last 3 ratings with scores and comments

### Action Buttons
- **Accept Application** - Accept this applicant
- **Reject** - Reject this applicant
- **View Profile** - See full profile

## 🎨 Visual Indicators

### Badges & Colors
- **New Doer Badge** - Purple badge with sparkles icon
- **Validated Skills** - Green badges with check-circle icon
- **Ranking Score** - Yellow/orange gradient background
- **Newbie Border** - Purple border around card

### Icons
- ⭐ Rating - Star icon
- ✅ Completed - Check-circle icon
- 🎁 Bonus - Gift icon
- 📄 Cover Letter - File-text icon
- 🕐 Timeline - Clock icon
- 🏆 Skills - Award icon
- 💬 Feedback - Message-square icon

## 🔄 Data Flow

### Task Ranking Flow
```
User views task dashboard
    ↓
get_matched_tasks_for_user() called
    ↓
Filter tasks by doer_type and skills
    ↓
Calculate priority scores:
  - Skill match
  - Poster rating (from Rating table)
  - Urgency
    ↓
Sort by priority_score DESC, created_at DESC
    ↓
Display tasks in order
```

### Applicant Ranking Flow
```
Task poster views applications
    ↓
view_applications() called
    ↓
Get all applications for task
    ↓
For each application:
  - Get real-time doer rating
  - Count completed tasks
  - Get validated skills
  - Calculate ranking score
    ↓
Sort by ranking_score DESC
    ↓
Separate by status (pending/accepted/rejected)
    ↓
Display with all details
```

## 📊 Database Queries

### Task Ranking Queries
```python
# Get poster rating
Rating.objects.filter(rated=OuterRef('poster')).aggregate(Avg('score'))

# Get tasks with annotations
Task.objects.filter(status='open').annotate(
    skill_match_score=...,
    urgency_score=...,
    poster_rating=...,
    priority_score=...
).order_by('-priority_score', '-created_at')
```

### Applicant Ranking Queries
```python
# Get doer rating
Rating.objects.filter(rated=OuterRef('doer')).aggregate(Avg('score'))

# Count completed tasks
Task.objects.filter(doer=..., status='completed').count()

# Get validated skills
StudentSkill.objects.filter(student=..., status='verified')

# Get recent ratings
Rating.objects.filter(rated=...).order_by('-created_at')[:3]
```

## ✨ Features

### Task Ranking
- ✅ Real-time poster ratings
- ✅ Skill-based matching
- ✅ Urgency detection
- ✅ Consistent sorting
- ✅ Fallback to creation date

### Applicant Ranking
- ✅ Real-time doer ratings
- ✅ Experience tracking
- ✅ Newbie bonus system
- ✅ Validated skills display
- ✅ Recent feedback preview
- ✅ Visual ranking indicators
- ✅ Smart sorting

## 🧪 Testing

### Test Task Ranking
1. Create 3 tasks with different poster ratings
2. Create a task doer with specific skills
3. View task dashboard
4. Verify tasks are sorted by priority score
5. Check that higher-rated posters' tasks appear first

### Test Applicant Ranking
1. Create a task as task poster
2. Have 3 different doers apply:
   - One with high rating and experience
   - One newbie with no ratings
   - One with moderate rating
3. View applications
4. Verify ranking order matches calculation
5. Check validated skills are displayed
6. Verify newbie bonus is applied

## 📁 Files Modified

- **`core/views.py`**
  - `get_matched_tasks_for_user()` - Task ranking (lines 216-312)
  - `view_applications()` - Applicant ranking (lines 2019-2113)

- **`core/templates/tasks/applications.html`**
  - Added validated skills display (lines 177-197)

## 🚀 Next Steps

1. Restart Django: `python manage.py runserver`
2. Create test tasks with different poster ratings
3. Create test applications from different doers
4. Verify ranking order in both views
5. Test with different skill combinations
6. Verify newbie bonus is applied correctly

## 📝 Notes

- **Real-time Ratings**: Ratings are calculated from the Rating table, not cached
- **Newbie Definition**: Less than 3 completed tasks
- **Skill Matching**: Only exact skill matches count (typing, powerpoint, graphics)
- **Urgency**: Tasks with deadline within 24 hours get urgency bonus
- **Sorting**: Primary sort by score, secondary sort by creation date

## 🎯 Benefits

✅ **Better Task Discovery** - Users see most relevant tasks first
✅ **Fair Applicant Selection** - Newbies get a fair chance
✅ **Transparent Ranking** - Users understand why tasks/applicants are ranked
✅ **Quality Assurance** - Higher-rated users are prioritized
✅ **Skill Verification** - Validated skills are visible
✅ **Experience Tracking** - Completed tasks are counted
✅ **Feedback Integration** - Recent ratings are shown
