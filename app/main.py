from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
from app.database import student_collection,teachers_collection,classes_collection
from bson import ObjectId
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.database import users_collection
from app.auth import hash_password, verify_password, create_access_token
from pathlib import Path

from fastapi import Depends

from app.auth import verify_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

app = FastAPI(
    title="School Management System",
    description="""
    API for managing a school's:

    - Students
    - Teachers
    - Classes

    This project uses FastAPI and MongoDB.
    """,
    version="1.0.0"
)

security = HTTPBearer(auto_error=False)
def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security)
):

    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Please provide an access token"
        )

    token = credentials.credentials

    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    return payload

def admin_only(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    return current_user
BASE_DIR = Path(__file__).resolve().parent.parent

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "frontend"),
    name="static"
)

@app.get("/")
def home():
    return FileResponse(BASE_DIR / "frontend" / "index.html")


class Student(BaseModel):
    name:str
    age:int
    class_id:str

@app.post("/students")
def create_student(student:Student,admin_user: dict = Depends(admin_only)):
    student_data=student.model_dump()
    
    if not ObjectId.is_valid(student.class_id):
       raise HTTPException(
        status_code=400,
        detail="Invalid Class ID"
    )

    school_class = classes_collection.find_one({
    "_id": ObjectId(student.class_id)
})

    if school_class is None:
        raise HTTPException(
        status_code=404,
        detail="Class not found"
    )

    result = student_collection.insert_one(student_data)
    student_data["_id"] = str(result.inserted_id)
    return{
        "message":"student created successfully",
        "student_id":str(result.inserted_id),
        "student":student_data
    }



@app.get("/students")
def get_students(
    current_user: dict = Depends(get_current_user)
):
    students = []

    for student in student_collection.find():
        school_class = None

        if student.get("class_id"):
            school_class = classes_collection.find_one({
                "_id": ObjectId(student["class_id"])
            })

        student["_id"] = str(student["_id"])

        if school_class:
            school_class["_id"] = str(school_class["_id"])
            student["class_details"] = school_class

        students.append(student)

    return {"students": students}
@app.get("/students/search")
def search_students(name: str):

    students = student_collection.find({
        "name": {"$regex": name, "$options": "i"}
    })

    result = []

    for student in students:
        student["_id"] = str(student["_id"])
        result.append(student)

    return {"students": result}


@app.get("/students/pagination")
def get_students_pagination(page: int = 1, limit: int = 5):

    if page < 1:
        raise HTTPException(
            status_code=400,
            detail="Page must be greater than 0"
        )

    if limit < 1:
        raise HTTPException(
            status_code=400,
            detail="Limit must be greater than 0"
        )

    total_records = student_collection.count_documents({})

    skip = (page - 1) * limit

    students = student_collection.find().skip(skip).limit(limit)

    result = []

    for student in students:
        student["_id"] = str(student["_id"])
        result.append(student)

    total_pages = (total_records + limit - 1) // limit

    return {
        "page": page,
        "limit": limit,
        "total_records": total_records,
        "total_pages": total_pages,
        "students": result
    }

@app.get("/teachers/search")
def search_teachers(subject: str,current_user: dict = Depends(get_current_user)):

    teachers = teachers_collection.find({
        "subject": {"$regex": subject, "$options": "i"}
    })

    result = []

    for teacher in teachers:
        teacher["_id"] = str(teacher["_id"])
        result.append(teacher)

    return {"teachers": result}


@app.get("/teachers/pagination")
def get_teachers_pagination(page: int = 1, limit: int = 5,current_user: dict = Depends(get_current_user)):


    if page < 1:
        raise HTTPException(status_code=400, detail="Page must be greater than 0")

    if limit < 1:
       raise HTTPException(status_code=400, detail="Limit must be greater than 0")
    skip = (page - 1) * limit

    teachers = teachers_collection.find().skip(skip).limit(limit)

    result = []

    for teacher in teachers:
        teacher["_id"] = str(teacher["_id"])
        result.append(teacher)

    return {
        "page": page,
        "limit": limit,
        "teachers": result
    }


@app.get("/classes/search")
def search_classes(class_name: str,current_user: dict = Depends(get_current_user)):

    classes = classes_collection.find({
        "class_name": {"$regex": class_name, "$options": "i"}
    })

    result = []

    for school_class in classes:
        school_class["_id"] = str(school_class["_id"])
        result.append(school_class)

    return {"classes": result}


@app.get("/classes/pagination")
def get_classes_pagination(page: int = 1, limit: int = 5,current_user: dict = Depends(get_current_user)):

    if page < 1:
       raise HTTPException(status_code=400, detail="Page must be greater than 0")

    if limit < 1:
       raise HTTPException(status_code=400, detail="Limit must be greater than 0")


    skip = (page - 1) * limit

    classes = classes_collection.find().skip(skip).limit(limit)

    result = []

    for school_class in classes:
        school_class["_id"] = str(school_class["_id"])
        result.append(school_class)

    return {
        "page": page,
        "limit": limit,
        "classes": result
    }


@app.get("/students/{student_id}")
def get_student(student_id: str,current_user: dict = Depends(get_current_user)):

    if not ObjectId.is_valid(student_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid student ID"
        )

    student = student_collection.find_one({
        "_id": ObjectId(student_id)
    })

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    school_class = classes_collection.find_one({
        "_id": ObjectId(student["class_id"])
    })

    student["_id"] = str(student["_id"])

    if school_class:
        school_class["_id"] = str(school_class["_id"])
        student["class_details"] = school_class

    return {"student": student}



@app.put("/students/{student_id}")
def update_student(student_id: str, student: Student,admin_user: dict = Depends(admin_only)):

    if not ObjectId.is_valid(student_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid Student ID"
        )

    if not ObjectId.is_valid(student.class_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid Class ID"
        )

    school_class = classes_collection.find_one({
        "_id": ObjectId(student.class_id)
    })

    if school_class is None:
        raise HTTPException(
            status_code=404,
            detail="Class not found"
        )

    result = student_collection.replace_one(
        {"_id": ObjectId(student_id)},
        student.model_dump()
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    return {"message": "Student updated successfully"}


class Studentupdate(BaseModel):
    name:str |None =None
    age:int |None = None
    class_id:str |None =None

    model_config={
        "json_schema_extra":{
            "example":{}
        }
    }


@app.patch("/students/{student_id}")
def patch_student(student_id: str, student: Studentupdate,admin_user: dict = Depends(admin_only)):

    if not ObjectId.is_valid(student_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid Student ID"
        )

    update_data = student.model_dump(exclude_unset=True)

    if "class_id" in update_data:
        if not ObjectId.is_valid(update_data["class_id"]):
            raise HTTPException(
                status_code=400,
                detail="Invalid Class ID"
            )

        school_class = classes_collection.find_one({
            "_id": ObjectId(update_data["class_id"])
        })

        if school_class is None:
            raise HTTPException(
                status_code=404,
                detail="Class not found"
            )

    result = student_collection.update_one(
        {"_id": ObjectId(student_id)},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    return {"message": "Student updated successfully"}



@app.delete("/students/{student_id}")
def delete_student(student_id: str,
    admin_user: dict = Depends(admin_only)):

    if not ObjectId.is_valid(student_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid Student ID"
        )

    result = student_collection.delete_one(
        {"_id": ObjectId(student_id)}
    )

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    return {
        "message": "Student deleted successfully"
    }




class Teacher(BaseModel):
    name:str
    age:int
    subject:str
    qualification:str

@app.post("/teachers")
def create_teacher(teacher:Teacher,admin_user: dict = Depends(admin_only)):
    teacher_data=teacher.model_dump()

    result=teachers_collection.insert_one(teacher_data)
    
    teacher_data["_id"]=str(result.inserted_id)

    return{
        "message":"teacher create successfully",
        "teacher":teacher_data
    }



@app.get("/teachers")
def get_teachers(current_user: dict = Depends(get_current_user)):
    teachers = []

    for teacher in teachers_collection.find():
        teacher["_id"] = str(teacher["_id"])
        teachers.append(teacher)

    return {"teacher": teachers}


@app.get("/teachers/{teacher_id}")
def get_teacher(teacher_id:str,current_user: dict = Depends(get_current_user)):
    if not ObjectId.is_valid(teacher_id):
        raise HTTPException(
            status_code=400,
            detail="invalid teacher id"
        )

    teacher = teachers_collection.find_one({
        "_id":ObjectId(teacher_id)
    })

    if teacher is None:
        raise HTTPException(
            status_code=404,
            detail="Teacher is not found"
        )


    teacher["_id"]=str(teacher["_id"])
    return {"Teacher":teacher}

@app.put("/teachers/{teacher_id}")
def update_teacher(teacher_id:str,teacher:Teacher,admin_user: dict = Depends(admin_only)):
    if not ObjectId.is_valid(teacher_id):
        raise HTTPException(
            status_code=400,
            detail="ID not found"
        )

    result = teachers_collection.replace_one(
        {"_id":ObjectId(teacher_id)},
        teacher.model_dump()
    )

    if result.matched_count==0:
        raise HTTPException(
            status_code=404,
            detail="Teacher not found"
        )

    return{"teacher":"teacher update successfully"}


class TeacherUpdate(BaseModel):
    name: str | None = None
    age: int | None = None
    subject: str | None = None
    qualification: str | None = None

    model_config = {
        "json_schema_extra": {
            "example": {}
        }
    }

@app.patch("/teachers/{teacher_id}")
def patch_teacher(teacher_id:str,teacher:TeacherUpdate,admin_user: dict = Depends(admin_only)):
    if not ObjectId.is_valid(teacher_id):
        raise HTTPException(
            status_code=400,
            detail="id not found"
        )

    update_data = teacher.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="Not found"
        )

    result = teachers_collection.update_one(
        {"_id":ObjectId(teacher_id)},
        {"$set":update_data}
    )

    if result.matched_count==0:
        raise HTTPException(
            status_code=404,
            detail="Teacher not found"
        )

    return{"message":"Teacher update successfully"}


@app.delete("/teachers/{teacher_id}")
def delete_teacher(teacher_id:str,admin_user: dict = Depends(admin_only)):
    if not ObjectId.is_valid(teacher_id):
        raise HTTPException(
            status_code=400,
            detail="ID not found"
        )

    result =teachers_collection.delete_one(
        {"_id":ObjectId(teacher_id)}
    )

    if result.deleted_count==0:
        raise HTTPException(
            status_code=404,
            detail="Teacher not found"
        )

    return{"message":"Teacher delete successfully"}


class SchoolClass(BaseModel):
    class_name: str
    section: str
    room_number: int

@app.post("/classes")
def create_class(scholl_class:SchoolClass,admin_user: dict = Depends(admin_only)):
    class_data=scholl_class.model_dump()
    result = classes_collection.insert_one(class_data)
    class_data["_id"]=str(result.inserted_id)
    return{
        "message":"create class successfully",
        "class":class_data
    }

@app.get("/classes")
def get_classes(current_user: dict = Depends(get_current_user)):

    classes = classes_collection.find()

    result = []

    for school_class in classes:
        school_class["_id"] = str(school_class["_id"])
        result.append(school_class)

    return {
        "total_classes": len(result),
        "classes": result
    }

@app.get("/classes/{class_id}")
def get_class(class_id:str,current_user: dict = Depends(get_current_user)):
    if not ObjectId.is_valid(class_id):
        raise HTTPException(
            status_code=400,
            detail="Id not found"
        )

    scholl_class = classes_collection.find_one(
        {"_id":ObjectId(class_id)}
    )

    if scholl_class is None:
        raise HTTPException(
            status_code=404,
            detail="Class not found"
        )

    scholl_class["_id"]=str(scholl_class["_id"])

    return scholl_class

@app.put("/classes/{class_id}")
def update_class(class_id:str,scholl_class:SchoolClass,admin_user: dict = Depends(admin_only)):
    if not ObjectId.is_valid(class_id):
        raise HTTPException(
            status_code=400,
            detail="Id not found"
        )

    result = classes_collection.replace_one(
        {"_id":ObjectId(class_id)},
        scholl_class.model_dump()
    )

    if result.matched_count==0:
        raise HTTPException(
            status_code=404,
            detail="Class not found"
        )

    return{"message":"update Successfully"}


class ClassUpdate(BaseModel):
    class_name: str | None = None
    section: str | None = None
    room_number: int | None = None

    model_config = {
        "json_schema_extra": {
            "example": {}
        }
    }

@app.patch("/classes/{class_id}")
def patch_class(class_id: str, scholl_class: ClassUpdate,admin_user: dict = Depends(admin_only)):

    if not ObjectId.is_valid(class_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid Class ID"
        )

    update_data = scholl_class.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="Please provide at least one field to update"
        )

    result = classes_collection.update_one(
        {"_id": ObjectId(class_id)},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Class not found"
        )

    return {"message": "Class updated successfully"}

@app.delete("/classes/{class_id}")
def delete_class(class_id:str,admin_user: dict = Depends(admin_only)):
    if not ObjectId.is_valid(class_id):
        raise HTTPException(
            status_code=400,
            detail="Id not found"
        )

    result = classes_collection.delete_one(
        {"_id":ObjectId(class_id)}
    )

    if result.deleted_count==0:
        raise HTTPException(
            status_code=404,
            detail="class not found"
        )

    return{"message":"Delete successfully"}












@app.get("/dashboard")
def get_dashboard():

    total_students = student_collection.count_documents({})
    total_teachers = teachers_collection.count_documents({})
    total_classes = classes_collection.count_documents({})

    return {
        "total_students": total_students,
        "total_teachers": total_teachers,
        "total_classes": total_classes
    }





class UserRegister(BaseModel):
    name: str
    email: str
    password: str

@app.post("/register")
def register_user(user: UserRegister):

    existing_user = users_collection.find_one({
        "email": user.email
    })

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    hashed_password = hash_password(user.password)

    new_user = {
        "name": user.name,
        "email": user.email,
        "hashed_password": hashed_password,
        "role": "user"
    }

    users_collection.insert_one(new_user)

    return {
        "message": "User registered successfully"
    }

class UserLogin(BaseModel):
    email: str
    password: str

@app.post("/login")
def login_user(user: UserLogin):

    existing_user = users_collection.find_one({
        "email": user.email
    })

    if not existing_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    password_correct = verify_password(
        user.password,
        existing_user["hashed_password"]
    )

    print("PASSWORD CORRECT:", password_correct)

    if not password_correct:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    token = create_access_token({
        "sub": str(existing_user["_id"]),
        "role": existing_user["role"]
    })
    print("TOKEN CREATED:", bool(token))

    return {
        "message": "Login successful",
        "access_token": token,
        "token_type": "bearer"
    }




@app.get("/profile")
def get_profile(current_user: dict = Depends(get_current_user)):

    return {
        "message": "You are logged in!",
        "user_id": current_user["sub"],
        "role": current_user["role"]
    }