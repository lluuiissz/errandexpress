# ErrandExpress API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
All endpoints (except `/health/` and public pages) require user authentication via Django session.

---

## Health Check

### GET /health/
Check system health status.

**Response (200 OK)**:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-24T11:32:00Z",
  "database": "connected",
  "cache": "connected"
}
```

**Response (503 Service Unavailable)**:
```json
{
  "status": "unhealthy",
  "timestamp": "2025-11-24T11:32:00Z",
  "error": "Database connection failed"
}
```

---

## Task Management

### POST /tasks/create/
Create a new task (Task Poster only).

**Request**:
```json
{
  "title": "Write essay",
  "description": "500-word essay on climate change",
  "category": "typing",
  "tags": "essay,urgent",
  "price": 150,
  "payment_method": "gcash",
  "deadline": "2025-11-25T17:00:00Z",
  "location": "Online",
  "requirements": "Good grammar, APA format"
}
```

**Response (302 Redirect)**:
Redirects to task detail page on success.

**Errors**:
- 400: Missing required fields
- 400: Price below minimum (₱10)
- 400: Deadline in the past
- 403: User is not a task poster

---

### GET /tasks/browse/
Browse available tasks with smart matching.

**Query Parameters**:
- `search`: Search by title/description/tags
- `category`: Filter by category (microtask, typing, powerpoint, graphics)
- `min_price`: Minimum price filter
- `max_price`: Maximum price filter
- `sort_by`: Sort order (created_at, -created_at, price, -price, deadline)
- `page`: Page number (default: 1)

**Response (200 OK)**:
```json
{
  "tasks": [
    {
      "id": "uuid",
      "title": "Write essay",
      "description": "500-word essay...",
      "price": 150,
      "category": "typing",
      "deadline": "2025-11-25T17:00:00Z",
      "poster": {
        "id": "uuid",
        "fullname": "John Doe",
        "avg_rating": 4.8
      },
      "status": "open",
      "priority_score": 8.5
    }
  ],
  "total": 42,
  "page": 1,
  "pages": 3
}
```

---

### GET /tasks/<task_id>/
Get task details.

**Response (200 OK)**:
```json
{
  "id": "uuid",
  "title": "Write essay",
  "description": "500-word essay on climate change",
  "category": "typing",
  "tags": "essay,urgent",
  "price": 150,
  "payment_method": "gcash",
  "deadline": "2025-11-25T17:00:00Z",
  "location": "Online",
  "requirements": "Good grammar, APA format",
  "status": "open",
  "poster": {
    "id": "uuid",
    "fullname": "John Doe",
    "avg_rating": 4.8,
    "total_ratings": 25
  },
  "doer": null,
  "created_at": "2025-11-24T10:00:00Z",
  "updated_at": "2025-11-24T10:00:00Z"
}
```

---

### PUT /tasks/<task_id>/edit/
Edit an existing task (Task Poster only, open tasks only).

**Request**:
Same as POST /tasks/create/

**Response (302 Redirect)**:
Redirects to task detail page on success.

**Errors**:
- 403: User is not the task poster
- 403: Task is not in open status
- 400: Validation errors

---

## Messaging

### POST /api/send-message/
Send a message in task chat.

**Request**:
```json
{
  "task_id": "uuid",
  "message": "I can complete this task"
}
```

**Response (200 OK)**:
```json
{
  "success": true,
  "message_id": "uuid",
  "created_at": "2025-11-24T11:32:00Z",
  "sender": "John Doe",
  "messages_remaining": 2
}
```

**Response (400 Bad Request)**:
```json
{
  "success": false,
  "error": "You have reached the 5-message limit. Please pay ₱2 system fee to continue chatting.",
  "payment_required": true
}
```

---

### GET /api/messages/<task_id>/
Fetch messages for a task (polling).

**Response (200 OK)**:
```json
{
  "success": true,
  "messages": [
    {
      "id": "uuid",
      "sender_id": "uuid",
      "sender_name": "John Doe",
      "message": "I can help with this",
      "created_at": "2025-11-24T11:30:00Z"
    }
  ],
  "count": 3
}
```

---

### GET /api/check-chat/<task_id>/
Check if user can access chat.

**Response (200 OK)**:
```json
{
  "allowed": true,
  "reason": "Chat access granted (paid)",
  "messages_used": 5,
  "paid": true
}
```

**Response (200 OK - Free tier)**:
```json
{
  "allowed": true,
  "reason": "Free messages remaining",
  "messages_remaining": 3,
  "free_tier": true
}
```

**Response (200 OK - Locked)**:
```json
{
  "allowed": false,
  "reason": "You have reached the 5-message limit. Please pay ₱2 system fee to continue chatting.",
  "payment_required": true,
  "messages_used": 5
}
```

---

## Payments

### POST /api/create-payment-intent/
Create PayMongo payment intent for ₱2 system fee.

**Request**:
```json
{
  "task_id": "uuid"
}
```

**Response (200 OK)**:
```json
{
  "data": {
    "id": "pi_xxx",
    "attributes": {
      "amount": 200,
      "currency": "PHP",
      "status": "awaiting_payment_method",
      "client_key": "key_xxx"
    }
  }
}
```

---

### POST /api/create-gcash-payment/
Create GCash payment source.

**Request**:
```json
{
  "task_id": "uuid"
}
```

**Response (200 OK)**:
```json
{
  "success": true,
  "checkout_url": "https://checkout.paymongo.com/...",
  "source_id": "src_xxx"
}
```

---

### POST /webhook/paymongo/
PayMongo webhook (automatic, no manual call needed).

**Handles**:
- `payment.paid`: Updates payment status, unlocks chat
- `source.chargeable`: Processes GCash payment

---

## Ratings

### POST /rate/<task_id>/<user_id>/
Rate a user after task completion.

**Request**:
```json
{
  "score": 9,
  "feedback": "Excellent work, very professional"
}
```

**Response (302 Redirect)**:
Redirects to task detail on success.

---

## Notifications

### GET /api/notifications/recent/
Get recent notifications (AJAX).

**Response (200 OK)**:
```json
{
  "success": true,
  "notifications": [
    {
      "id": "uuid",
      "type": "task_assigned",
      "title": "Task Assigned",
      "message": "You have been assigned to 'Write essay'",
      "created_at": "2025-11-24T11:30:00Z",
      "is_read": false
    }
  ],
  "count": 5
}
```

---

### GET /api/notifications/count/
Get unread notification count.

**Response (200 OK)**:
```json
{
  "success": true,
  "count": 3
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "Invalid request data",
  "details": "Field 'title' is required"
}
```

### 401 Unauthorized
```json
{
  "error": "Authentication required"
}
```

### 403 Forbidden
```json
{
  "error": "You don't have permission to perform this action"
}
```

### 404 Not Found
```json
{
  "error": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "An error occurred while processing your request"
}
```

---

## Rate Limiting

Currently no rate limiting is enforced. Recommended limits:
- `/api/send-message/`: 10 requests per minute per user
- `/api/create-payment-intent/`: 5 requests per minute per user
- `/api/notifications/`: 30 requests per minute per user

---

## Pagination

Default page size: 20 items

**Query Parameters**:
- `page`: Page number (default: 1)

**Response**:
```json
{
  "results": [...],
  "count": 42,
  "next": "http://localhost:8000/tasks/browse/?page=2",
  "previous": null
}
```

---

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK |
| 201 | Created |
| 302 | Redirect |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

---

## Testing

Run tests:
```bash
python manage.py test core
```

Run specific test:
```bash
python manage.py test core.tests.TaskCreationTests.test_create_task_with_all_fields
```

---

## Changelog

### v1.0 (2025-11-24)
- Initial API documentation
- Health check endpoint
- Task CRUD operations
- Messaging system
- Payment integration
- Rating system
- Notification system
