# ErrandExpress - Task Marketplace Platform

A full-stack Django + React application for connecting task posters with task doers. Features smart task ranking, applicant selection, real-time messaging, and integrated payment processing.

## 🚀 Features

### Task Management
- **Smart Task Ranking** - Tasks ranked by poster rating, skill match, and urgency
- **3-Minute Application Window** - Multiple doers can apply within 3 minutes
- **Task Categories** - Microtasks, Typing, PowerPoint, Graphics Design
- **Real-time Status** - Open, In Progress, Completed, Cancelled

### Applicant System
- **Intelligent Ranking** - Applicants ranked by rating, experience, and newbie bonus
- **Validated Skills Display** - Show verified skills with badges
- **Recent Feedback** - Display last 3 ratings for each applicant
- **Fair Selection** - Newbie bonus encourages new doers

### User System
- **Dual Roles** - Task Posters and Task Doers
- **Skill Validation** - Typing test, PowerPoint, Graphics Design verification
- **Rating System** - 1-10 scale with feedback
- **User Profiles** - Complete profile management

### Communication
- **Real-time Chat** - Embedded chat between poster and doer
- **Typing Indicators** - See when someone is typing
- **Message Polling** - Optimized 5-second polling
- **Chat Unlocking** - Automatic unlock on payment

### Payments
- **PayMongo Integration** - GCash and Card payments
- **System Commission** - ₱2 fee per task
- **Payment Methods** - Cash on Delivery (COD) and Online Payment
- **Webhook Confirmation** - Real-time payment verification
- **System Wallet** - Track earnings and spending

### Admin Features
- **Admin Dashboard** - Monitor all activities
- **Skill Validation** - Approve/reject skill submissions
- **Payment Tracking** - View all transactions
- **Audit Logs** - Complete action history
- **User Management** - Manage users and roles

## 📋 Tech Stack

### Backend
- **Django 4.2** - Web framework
- **Django REST Framework** - API endpoints
- **PostgreSQL/SQLite** - Database
- **Celery** - Task queue
- **Redis** - Caching

### Frontend
- **HTML5/CSS3** - Markup and styling
- **Tailwind CSS** - Utility-first CSS
- **Lucide Icons** - Icon library
- **JavaScript** - Client-side logic
- **Fetch API** - HTTP requests

### External Services
- **PayMongo** - Payment processing
- **Vercel** - Serverless deployment
- **Supabase** - PostgreSQL database

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- pip
- Git
- PostgreSQL (optional, SQLite for development)

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/errandexpress.git
cd ErrandExpressv2
```

2. **Create virtual environment**
```bash
py -m venv venv
venv\Scripts\activate
```

3. **Install dependencies**
```bash
cd errandexpress
pip install -r requirements.txt
```

4. **Create .env file**
```bash
cp .env.example .env
```

5. **Configure environment variables**
```
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
PAYMONGO_SECRET_KEY=your-paymongo-key
PAYMONGO_PUBLIC_KEY=your-paymongo-public-key
```

6. **Run migrations**
```bash
py manage.py migrate
```

7. **Create superuser**
```bash
py manage.py createsuperuser
```

8. **Collect static files**
```bash
py manage.py collectstatic --noinput
```

9. **Run development server**
```bash
py manage.py runserver
```

Visit `http://localhost:8000` in your browser.

## 🚀 Deployment to Vercel

### Prerequisites
- Vercel account (free at https://vercel.com)
- GitHub account
- Git installed

### Quick Start

1. **Push to GitHub**
```bash
git add .
git commit -m "Ready for Vercel deployment"
git push origin main
```

2. **Connect to Vercel**
- Go to https://vercel.com
- Click "New Project"
- Select your GitHub repository
- Click "Import"

3. **Set Environment Variables**
In Vercel dashboard → Settings → Environment Variables, add:
- `DJANGO_SECRET_KEY` - Your Django secret key
- `DATABASE_URL` - Supabase PostgreSQL connection
- `DEBUG` - Set to `False`
- `ALLOWED_HOSTS` - Your Vercel domain
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_KEY` - Your Supabase API key
- `PAYMONGO_SECRET_KEY` - PayMongo secret key
- `PAYMONGO_PUBLIC_KEY` - PayMongo public key
- `PAYMONGO_WEBHOOK_SECRET` - PayMongo webhook secret

4. **Deploy**
- Click "Deploy"
- Vercel will build and deploy automatically
- Your app will be live at `https://your-project.vercel.app`

### Post-Deployment
- Update PayMongo webhook URL to your Vercel domain
- Set up custom domain (optional)
- Monitor logs in Vercel dashboard

**For detailed instructions, see `VERCEL_DEPLOYMENT_GUIDE.md`**

## 📚 API Documentation

### Authentication
- `POST /api/auth/login/` - Login
- `POST /api/auth/signup/` - Register
- `POST /api/auth/logout/` - Logout

### Tasks
- `GET /api/tasks/` - List tasks
- `POST /api/tasks/` - Create task
- `GET /api/tasks/{id}/` - Get task details
- `PUT /api/tasks/{id}/` - Update task
- `DELETE /api/tasks/{id}/` - Delete task

### Applications
- `GET /api/tasks/{id}/applications/` - List applications
- `POST /api/tasks/{id}/apply/` - Apply for task
- `PUT /api/applications/{id}/` - Update application status

### Messages
- `GET /api/messages/` - List messages
- `POST /api/messages/` - Send message
- `GET /api/messages/poll/` - Poll for new messages

### Payments
- `POST /api/payments/` - Create payment
- `GET /api/payments/{id}/` - Get payment status
- `POST /webhook/paymongo/` - PayMongo webhook

## 🧪 Testing

### Run Tests
```bash
py manage.py test
```

### Test Coverage
```bash
coverage run --source='.' manage.py test
coverage report
```

### Manual Testing
1. Create task as task_poster
2. Apply as task_doer
3. View applications
4. Accept/reject applications
5. Start chat
6. Complete task
7. Rate user

## 📊 Database Schema

### Core Models
- **User** - User accounts (task_poster, task_doer, admin)
- **Task** - Task listings
- **TaskApplication** - Applications from doers
- **Message** - Chat messages
- **Rating** - User ratings
- **StudentSkill** - Validated skills
- **Payment** - Payment records
- **SystemCommission** - System fees
- **Notification** - User notifications

## 🔐 Security

- CSRF protection enabled
- SQL injection prevention (Django ORM)
- XSS protection (template escaping)
- Password hashing (Django default)
- Secure session management
- HTTPS recommended for production
- API authentication via session/token

## 📝 Configuration

### Settings
- `DEBUG` - Development mode
- `SECRET_KEY` - Django secret key
- `ALLOWED_HOSTS` - Allowed domains
- `DATABASES` - Database configuration
- `INSTALLED_APPS` - Django apps
- `MIDDLEWARE` - Request/response middleware

### PayMongo
- Set `PAYMONGO_SECRET_KEY` in environment
- Set `PAYMONGO_PUBLIC_KEY` in environment
- Configure webhook URL in PayMongo dashboard
- Test with test keys first

## 🐛 Troubleshooting

### Database Issues
```bash
# Reset database
py manage.py migrate zero core
py manage.py migrate

# Create superuser
py manage.py createsuperuser
```

### Static Files
```bash
# Collect static files
py manage.py collectstatic --noinput

# Clear cache
py manage.py clear_cache
```

### Payment Issues
- Verify PayMongo keys
- Check webhook URL
- Review payment logs
- Test with test payment

## 📞 Support

For issues and questions:
1. Check documentation files
2. Review error logs
3. Check Django debug page (development)
4. Contact admin

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 👥 Contributors

- Admin Team
- Development Team

## 🎯 Roadmap

- [ ] Mobile app (React Native)
- [ ] Video chat integration
- [ ] Advanced analytics
- [ ] Machine learning recommendations
- [ ] Blockchain payments
- [ ] Multi-language support

## 📖 Documentation

- `VERCEL_DEPLOYMENT_GUIDE.md` - Complete Vercel deployment guide
- `TASK_AND_APPLICANT_RANKING.md` - Ranking system details
- `PAYMENT_FIX_SUMMARY.md` - Payment system overview
- `WEBHOOK_SETUP_GUIDE.md` - Webhook configuration
- `API_DOCUMENTATION.md` - API reference
- `QUICK_START_PAYMENT_TESTING.md` - Payment testing guide

---

**Made with ❤️ by ErrandExpress Team**
