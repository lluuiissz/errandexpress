# 🔧 Field Type Mismatch Fix - view_applications ✅

## Problem

**Error**: `FieldError: Expression contains mixed types: DecimalField, FloatField. You must set output_field.`

**Location**: `/tasks/<task_id>/applications/` page

**Root Cause**: Type mismatch in `Coalesce` function mixing `DecimalField` and `FloatField`

---

## The Issue

In the `view_applications()` function, the `Coalesce` expression was mixing two different field types:

```python
# ❌ WRONG: Mixing DecimalField and FloatField
doer_current_rating=Coalesce(
    Subquery(doer_rating_subquery, output_field=DecimalField(max_digits=3, decimal_places=2)),
    0.0  # This is a FloatField!
)
```

**Why it fails**:
- `Subquery` returns `DecimalField` (from `Avg('score')`)
- `0.0` is a `FloatField` (Python float)
- Django can't coalesce different field types without explicit output_field

---

## The Fix

**File**: `core/views.py` (lines 2160-2170)

**Solution**: Specify output_field for both the Value and Coalesce

```python
# ✅ CORRECT: Explicit field types
doer_current_rating=Coalesce(
    Subquery(doer_rating_subquery, output_field=DecimalField(max_digits=3, decimal_places=2)),
    Value(0.0, output_field=DecimalField(max_digits=3, decimal_places=2)),  # ✅ Explicit type
    output_field=DecimalField(max_digits=3, decimal_places=2)  # ✅ Explicit output
)
```

**What changed**:
1. Wrapped `0.0` in `Value()` with explicit `DecimalField`
2. Added `output_field` parameter to `Coalesce`
3. All types now match: `DecimalField`

---

## Why This Works

Django's ORM needs to know:
1. **What type each expression returns** → `output_field` on `Value`
2. **What type the final result should be** → `output_field` on `Coalesce`

By specifying both, Django can properly coalesce the values without type confusion.

---

## Code Changes

### Before ❌
```python
applications = applications.annotate(
    doer_current_rating=Coalesce(
        Subquery(doer_rating_subquery, output_field=DecimalField(max_digits=3, decimal_places=2)),
        0.0  # FloatField - type mismatch!
    ),
    doer_completed_count=Count(
        'doer__assigned_tasks',
        filter=Q(doer__assigned_tasks__status='completed')
    )
)
```

### After ✅
```python
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
```

---

## Testing

✅ Navigate to `/tasks/<task_id>/applications/`
✅ Page should load without errors
✅ See list of applicants with ratings
✅ Applicants ranked by score
✅ All ratings display correctly

---

## Related Imports

The fix uses imports already available in the file:
- `Value` - Line 20 (already imported)
- `DecimalField` - Line 19 (already imported)
- `Coalesce` - Line 23 (already imported)

No new imports needed!

---

## Status

✅ **FIXED** - Type mismatch resolved
✅ **TESTED** - Applications page now loads
✅ **OPTIMIZED** - Still uses prefetch_related for performance

---

## Summary

The issue was a simple type mismatch in the `Coalesce` function. By explicitly specifying the `DecimalField` type for both the `Value` and the `Coalesce` output, Django can properly handle the expression without errors.

The fix is minimal, non-breaking, and maintains all existing optimizations! 🎉
