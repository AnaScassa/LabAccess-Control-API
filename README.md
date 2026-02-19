# 🧪 Laboratory Access Control API
A Django REST API built with asynchronous processing using Celery + Redis, designed to solve a real-world laboratory access validation problem.

---

## 📌 Problem
In the laboratory where I work, it is necessary to verify:
- Whether a person actually rented the equipment they are using (handled in another application)
- How long the person stayed inside the laboratory
- Whether the identified individual matches a previously registered institutional user
The rental system already exists in another application.  
This project focuses on validating laboratory stay duration and linking access records to registered users.

---

## 🎯 Project Goal
- Process `.xls` files containing laboratory access records
- Identify users based on registration number (matricula)
- Automatically link them to users stored in an external JSON
- Calculate how long the user stayed in the lab
- Perform heavy processing asynchronously using Celery
- Prevent API blocking during file processing

---

## 🏗️ Architecture
- Backend: Django
- API: Django REST Framework
- Async Processing: Celery
- Message Broker: Redis
- Authentication: JWT + API Key
- External Integration: JSON-based user dataset
- Database: PostgreSQL/MySQL

---

## 🔄 System Flow
1. A `.xls` file is uploaded through an API endpoint  
2. The API validates the file  
3. A Celery task is triggered  
4. The task:
   - Reads the file
   - Creates or updates users
   - Attempts to link them with existing JSON users
   - Calculates stay duration
5. The processing status can be checked via endpoint  

---

## ⚙️ Implemented Features
- File upload via API  
- Asynchronous processing with Celery  
- Worker monitoring  
- Automatic linking by registration number  
- Name similarity matching (fuzzy matching)  
- Stay duration calculation  
- JWT-based authentication  
- Permission control  

---

## 🧠 Linking Strategy
The system attempts user linking in two steps:

1. By registration number  
2. By name similarity (fuzzy matching with configurable score threshold, e.g., 80%)

This reduces inconsistencies and manual registration errors.

---

## 🚀 Running the Project
1️⃣ Clone the repository
git clone <repository-url>
cd lab-access-api
2️⃣ Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
3️⃣ Install dependencies
pip install -r requirements.txt
4️⃣ Start Redis
redis-server
5️⃣ Run migrations
python manage.py migrate
6️⃣ Start Django server
python manage.py runserver
7️⃣ Start Celery worker
celery -A core worker --loglevel=info

---

## 🔐 Security
- JWT authentication
- API Key permission for internal integrations
- Protected endpoints
- File type validation

---

## 📈 Future Improvements
- Direct integration with the rental system
- Admin dashboard
- Visual task monitoring
- Structured logging
- Docker deployment
- Automated tests

