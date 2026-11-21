# School Management System

A web-based School Management System built using **Python, FastAPI, MongoDB, and HTML, CSS, JavaScript**.

## Features

- Student Management (Create, Read, Update, Delete)
- Teacher Management (Create, Read, Update, Delete)
- Class Management (Create, Read, Update, Delete)
- Search Students, Teachers, and Classes
- Pagination for records
- Dashboard with total Students, Teachers, and Classes
- MongoDB Atlas Database Integration
- RESTful APIs
- Interactive Admin Dashboard
- API Documentation with Swagger UI

## Technologies Used

- Python
- FastAPI
- MongoDB Atlas
- PyMongo
- HTML
- CSS
- JavaScript
- Uvicorn

## Project Structure

```text
SchoolManagementSystem/
│
├── app/
│   ├── main.py
│   ├── database.py
│   └── test_mongodb.py
│
├── frontend/
│   └── index.html
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/asadrehman914/School-Management-System.git
```

### 2. Open Project Folder

```bash
cd School-Management-System
```

### 3. Create Virtual Environment

```bash
python -m venv .venv
```

### 4. Activate Virtual Environment

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure Environment Variables

Create a `.env` file and add your MongoDB connection string:

```env
MONGO_URI=your_mongodb_connection_string
```

Never share your database credentials publicly.

### 7. Run the Application

```bash
python -m uvicorn app.main:app --reload
```

## Application URLs

| Page | URL |
|---|---|
| Admin Dashboard | http://127.0.0.1:8000/ |
| Swagger API Docs | http://127.0.0.1:8000/docs |
| API Health | http://127.0.0.1:8000/dashboard |

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/students` | Create Student |
| GET | `/Students` | Get All Students |
| GET | `/students/{student_id}` | Get Student |
| PUT | `/students/{student_id}` | Replace Student |
| PATCH | `/students/{student_id}` | Update Student |
| DELETE | `/students/{student_id}` | Delete Student |
| POST | `/teachers` | Create Teacher |
| GET | `/teachers` | Get All Teachers |
| POST | `/classes` | Create Class |
| GET | `/classes` | Get All Classes |
| GET | `/dashboard` | Dashboard Statistics |

## Author

**Asad Rehman**

GitHub: https://github.com/asadrehman914

---

This project was developed as a practical learning project to understand Python backend development, FastAPI, MongoDB, and REST APIs.