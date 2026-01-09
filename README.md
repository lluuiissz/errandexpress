# ErrandExpress 🚀

> A secure task marketplace platform connecting task posters with skilled doers

[![Django](https://img.shields.io/badge/Django-4.2.7-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.12.2-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supabase-blue.svg)](https://supabase.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Secure Commission System](#secure-commission-system)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [System Architecture](#system-architecture)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

**ErrandExpress** is a gig economy platform that facilitates trusted transactions between task posters and task doers. Similar to TaskRabbit or Fiverr, it provides a secure marketplace for local services, errands, and micro-tasks.

### What Makes ErrandExpress Different?

- **🔒 Secure Commission System**: 10% commission paid upfront before messaging
- **💬 Chat Lock**: Prevents platform bypass through contact info exchange
- **✅ Skill Validation**: Verified skills through automated testing
- **💰 Transparent Pricing**: Clear commission breakdown (90% to doer, 10% to platform)
- **🇵🇭 Local Payment**: Integrated with PayMongo for Philippine payments

---

## ✨ Key Features

### For Task Posters

- ✅ **Create Tasks** - Post tasks with detailed descriptions, pricing, and deadlines
- ✅ **Browse Applicants** - Review doer profiles, ratings, and validated skills
- ✅ **Secure Messaging** - Chat with doers after commission payment
- ✅ **Safe Payments** - Pay through GCash or credit/debit cards
- ✅ **Rate & Review** - Build trust through transparent feedback

### For Task Doers

- ✅ **Find Work** - Browse tasks matching your skills and location
- ✅ **Skill Validation** - Prove your expertise through automated tests
- ✅ **Flexible Income** - Choose tasks that fit your schedule
- ✅ **Guaranteed Payment** - Secure payment system protects your earnings
- ✅ **Build Reputation** - Earn ratings and grow your profile

### For the Platform

- ✅ **Revenue Protection** - 10% commission secured before contact
- ✅ **Fraud Prevention** - Chat lock prevents off-platform transactions
- ✅ **Trust Building** - Rating system ensures quality
- ✅ **Scalable Model** - Commission grows with platform

---

## 🔒 Secure Commission System

### How It Works

```
1. Task Created (₱100)
   ↓
2. Doer Accepts Task
   ↓
3. Poster Pays ₱10 Commission (10%)
   ↓
4. Chat Unlocks - Unlimited Messaging
   ↓
5. Task Completed
   ↓
6. Poster Pays ₱90 to Doer
```

### Why Commission Before Messaging?

**Problem:** Users could exchange contact info in free messages and complete transactions off-platform.

**Solution:** Require commission payment BEFORE the first message.

**Benefits:**
- ✅ Platform revenue secured upfront
- ✅ Prevents bypass through contact exchange
- ✅ All transactions stay on platform
- ✅ Users can't complete deals off-platform

### Payment Breakdown

For a ₱100 task:
- **Total Task Amount:** ₱100
- **Commission (10%) - Paid First:** ₱10
- **Doer Receives - Paid After Completion:** ₱90

**Total Poster Pays:** ₱100  
**Platform Revenue:** ₱10 (10%)  
**Doer Receives:** ₱90 (90%)

---

## 🛠️ Tech Stack

### Backend
- **Framework:** Django 4.2.7
- **Language:** Python 3.12.2
- **Database:** PostgreSQL (Supabase)
- **Backup DB:** MySQL (XAMPP)
- **Authentication:** Django Auth + Sessions

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Vanilla CSS (responsive design)
- **JavaScript** - Vanilla JS
- **Icons:** Lucide Icons

### Payment Integration
- **PayMongo** - Philippine payment gateway
- **Methods:** GCash, Credit/Debit Cards

### Infrastructure
- **Cloud Database:** Supabase (PostgreSQL)
- **Local Backup:** MySQL via XAMPP
- **Dual-Write System:** Automatic backup replication

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12.2 or higher
- PostgreSQL (or Supabase account)
- MySQL (XAMPP) - Optional for backup
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/lluuiissz/errandexpress.git
   cd errandexpress
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   cd errandexpress
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your credentials:
   ```env
   # Database
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   
   # Payment
   PAYMONGO_PUBLIC_KEY=your_paymongo_public_key
   PAYMONGO_SECRET_KEY=your_paymongo_secret_key
   
   # Django
   SECRET_KEY=your_django_secret_key
   DEBUG=True
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Frontend: http://127.0.0.1:8000/
   - Admin: http://127.0.0.1:8000/admin/

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    USER INTERFACE                        │
│  (Web Browser - Responsive Design)                      │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                  DJANGO APPLICATION                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Views      │  │   Models     │  │  Templates   │ │
│  │  (Logic)     │  │  (Data)      │  │   (UI)       │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                    DATA LAYER                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  PostgreSQL  │  │    MySQL     │  │  Supabase    │ │
│  │  (Primary)   │  │  (Backup)    │  │  (Cloud)     │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              EXTERNAL SERVICES                           │
│  ┌──────────────┐  ┌──────────────┐                    │
│  │   PayMongo   │  │    Email     │                    │
│  │  (Payment)   │  │ (Notifications)│                  │
│  └──────────────┘  └──────────────┘                    │
└─────────────────────────────────────────────────────────┘
```

### Database Models

**Core Models:**
- `User` - User accounts (posters and doers)
- `Task` - Task information and status
- `TaskApplication` - Task applications
- `Message` - Chat messages
- `SystemCommission` - Commission tracking
- `SystemWallet` - Platform revenue
- `Notification` - User notifications
- `Rating` - Reviews and ratings
- `Skill` - User skills and validation

---

## 📚 API Documentation

### Authentication

```
POST   /signup/          # Register new user
POST   /login/           # Login
POST   /logout/          # Logout
GET    /profile/         # View profile
```

### Tasks

```
GET    /tasks/browse/              # Browse tasks
GET    /tasks/<task_id>/           # Task details
POST   /tasks/create/              # Create task
POST   /tasks/<task_id>/accept/    # Accept task
POST   /tasks/<task_id>/complete/  # Mark complete
```

### Messaging

```
GET    /messages/                  # List conversations
GET    /messages/<task_id>/        # View chat
POST   /tasks/<task_id>/message/   # Send message
```

### Payments

```
GET    /payment/commission/<task_id>/     # Commission payment
POST   /payment/commission/<task_id>/     # Process commission
GET    /payment/task-doer/<task_id>/      # Doer payment
POST   /payment/task-doer/<task_id>/      # Process doer payment
```

---

## 🔐 Security Features

- **Password Hashing:** PBKDF2 with salt
- **CSRF Protection:** Django middleware
- **XSS Prevention:** Template auto-escaping
- **SQL Injection Prevention:** Django ORM
- **Payment Security:** PayMongo PCI compliance
- **Chat Lock:** Commission required before messaging
- **Session Management:** Secure cookie handling

---

## 📱 User Flows

### Task Poster Flow

1. Create account / Login
2. Create task with details and pricing
3. Review applications from doers
4. Accept one applicant
5. **Pay ₱10 commission to unlock chat**
6. Chat with doer about task details
7. Doer completes task
8. Pay ₱90 to doer
9. Rate and review doer

### Task Doer Flow

1. Create account / Login
2. Validate skills (optional)
3. Browse available tasks
4. Apply for tasks
5. Get accepted by poster
6. **Wait for poster to pay commission**
7. Chat with poster after commission paid
8. Complete task
9. Receive ₱90 payment
10. Rate and review poster

---

## 🧪 Testing

### Run Tests
```bash
python manage.py test
```

### Test Coverage
```bash
coverage run --source='.' manage.py test
coverage report
```

### Manual Testing Checklist

- [ ] Create task with ₱100 price
- [ ] Verify commission calculated as ₱10
- [ ] Apply for task as doer
- [ ] Accept application as poster
- [ ] Try to send message (should be locked)
- [ ] Pay ₱10 commission
- [ ] Verify chat unlocks
- [ ] Send unlimited messages
- [ ] Complete task
- [ ] Pay ₱90 to doer
- [ ] Verify system wallet has ₱10

---

## 📊 Project Status

**Version:** 2.0.0 - Secure Commission System  
**Status:** Active Development  
**Last Updated:** January 9, 2026

### Recent Updates

- ✅ Implemented secure commission-before-messaging system
- ✅ Removed "5 free messages" vulnerability
- ✅ Added commission payment page
- ✅ Updated chat lock UI
- ✅ Fixed template syntax errors
- ✅ Added comprehensive documentation

### Roadmap

- [ ] Mobile app (React Native)
- [ ] Email notifications
- [ ] SMS notifications
- [ ] Advanced search filters
- [ ] Task categories expansion
- [ ] Admin analytics dashboard
- [ ] Dispute resolution system

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Contribution Guidelines

- Follow PEP 8 style guide for Python
- Write meaningful commit messages
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting PR

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Team

**Developer:** Luis  
**GitHub:** [@lluuiissz](https://github.com/lluuiissz)  
**Repository:** [errandexpress](https://github.com/lluuiissz/errandexpress)

---

## 📞 Support

For support, email: [your-email@example.com]  
For bugs and feature requests, please [open an issue](https://github.com/lluuiissz/errandexpress/issues)

---

## 🙏 Acknowledgments

- Django community for the excellent framework
- PayMongo for payment integration
- Supabase for database hosting
- Lucide for beautiful icons
- All contributors and testers

---

## 📸 Screenshots

### Home Page
![Home Page](screenshots/home.png)

### Browse Tasks
![Browse Tasks](screenshots/browse.png)

### Chat Interface
![Chat](screenshots/chat.png)

### Commission Payment
![Payment](screenshots/payment.png)

---

**Made with ❤️ in the Philippines**
