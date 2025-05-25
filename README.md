# 🛠️ DRF App Setup Guide

## 📄 Neofi Assignment Link

📘 [Neofi Assignment Document](https://docs.google.com/document/d/1kPhppih_OrYvj_dzzoJIfw6KUL6oK-J35G3z9lc-ois/edit?tab=t.0)

---
## 📚 Helpful Guides written by coderraj07

* 🔗 [Complete Django Backend Setup Guide (Project Init to Auth)](https://coderraj07.medium.com/complete-django-backend-setup-guide-from-project-initialization-to-advanced-views-authentication-cc1ab54f7521)
* 🔗 [Managing Python Environments – Conda vs. venv](https://medium.com/towardsdev/managing-python-environments-the-right-way-conda-vs-venv-1691162a7016)

---

## 📦 Requirements

* Python 3.x
* Conda
* PostgreSQL (NeonDB)
* Redis

---

## ⚙️ Step-by-Step Setup

### 1. Clone the Repository

```bash
git clone https://github.com/coderRaj07/neofi_backend_assignment
cd neofi_backend_assignment
```

### 2. Create and Activate Conda Environment

```bash
conda create --name drf_env python=3.12
conda activate drf_env
```

### 3. Install Requirements

```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Variables

Create a `.env` file in the root directory and add the following:

```env
DJANGO_SECRET_KEY="your_django_secret_key"
DATABASE_URL="your_neondb_database_url"
REDIS_URL="your_redis_url"
```

---

## 🗃️ Database Setup

### 1. Create Migration Folders

```bash
python manage.py makemigrations users
python manage.py makemigrations events
```

### 2. Apply Migrations

```bash
python manage.py migrate
```

---

## 🚀 Run the Development Server

```bash
python manage.py runserver
```

---

## 📬 Postman Collection

🧪 [View Postman Collection](neofi_backend_assignment.postman_collection.json)

---

## ✅ Implemented & Tested Endpoints

### 🔐 Authentication

* [x] `POST /api/auth/register` – Register a new user
* [x] `POST /api/auth/login` – Login and receive an authentication token
* [x] `POST /api/auth/refresh` – Refresh an authentication token
* [x] `POST /api/auth/logout` – Invalidate the current token

### 📅 Event Management

* [x] `POST /api/events` – Create a new event
* [x] `GET /api/events` – List all events with pagination and filtering
* [x] `GET /api/events/{id}` – Get a specific event by ID
* [x] `PUT /api/events/{id}` – Update an event by ID
* [x] `DELETE /api/events/{id}` – Delete an event by ID
* [x] `POST /api/events/batch` – Create multiple events in a single request

### 🤝 Collaboration

* [x] `POST /api/events/{id}/share` – Share an event with other users
* [x] `GET /api/events/{id}/permissions` – List all permissions for an event
* [x] `PUT /api/events/{id}/permissions/{userId}` – Update permissions for a user
* [x] `DELETE /api/events/{id}/permissions/{userId}` – Remove access for a user

---

## 🚧 Not Yet Tested

### 🕓 Version History

* [ ] `GET /api/events/{id}/history/{versionId}` – Get a specific version of an event
* [ ] `POST /api/events/{id}/rollback/{versionId}` – Rollback to a previous version

### 📝 Changelog & Diff

* [ ] `GET /api/events/{id}/changelog` – Get a chronological log of changes
* [ ] `GET /api/events/{id}/diff/{versionId1}/{versionId2}` – Get a diff between two versions

---
