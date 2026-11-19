from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
from app.database import student_collection,teachers_collection,classes_collection
from bson import ObjectId
app = FastAPI(
    title="School Management system"
)

class Student(BaseModel):
    name:str
    age:int
    class_id:str

@app.post("/students")
def create_student(student:Student):
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



@app.get("/Students")
def get_students():
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

    return {
        "students": students
    }


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
def search_teachers(subject: str):

    teachers = teachers_collection.find({
        "subject": {"$regex": subject, "$options": "i"}
    })

    result = []

    for teacher in teachers:
        teacher["_id"] = str(teacher["_id"])
        result.append(teacher)

    return {"teachers": result}


@app.get("/teachers/pagination")
def get_teachers_pagination(page: int = 1, limit: int = 5):


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
def search_classes(class_name: str):

    classes = classes_collection.find({
        "class_name": {"$regex": class_name, "$options": "i"}
    })

    result = []

    for school_class in classes:
        school_class["_id"] = str(school_class["_id"])
        result.append(school_class)

    return {"classes": result}


@app.get("/classes/pagination")
def get_classes_pagination(page: int = 1, limit: int = 5):

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
def get_student(student_id: str):

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
def update_student(student_id: str, student: Student):

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
def patch_student(student_id: str, student: Studentupdate):

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
def delete_student(student_id: str):

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
def create_teacher(teacher:Teacher):
    teacher_data=teacher.model_dump()

    result=teachers_collection.insert_one(teacher_data)
    
    teacher_data["_id"]=str(result.inserted_id)

    return{
        "message":"teacher create successfully",
        "teacher":teacher_data
    }


@app.get("/teachers")
def get_teachers():
    teachers=[]

    for teacher in teachers_collection.find():
        teacher["_id"]=str(teacher["_id"])

        teachers.append(teacher)

        return{"teacher":teachers}

@app.get("/teachers/{teacher_id}")
def get_teacher(teacher_id:str):
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

@app.put("/teacher/{teacher_id}")
def update_teacher(teacher_id:str,teacher:Teacher):
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

@app.patch("/teachers{teacher_id}")
def patch_teacher(teacher_id:str,teacher:TeacherUpdate):
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
def delete_teacher(teacher_id:str):
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
def create_class(scholl_class:SchoolClass):
    class_data=scholl_class.model_dump()
    result = classes_collection.insert_one(class_data)
    class_data["_id"]=str(result.inserted_id)
    return{
        "message":"create class successfully",
        "class":class_data
    }

@app.get("/classes")
def get_classes():

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
def get_class(class_id:str):
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

@app.put("/class/{class_id}")
def update_class(class_id:str,scholl_class:SchoolClass):
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

@app.patch("/class/{class_id}")
def patch_class(class_id:str,scholl_class:ClassUpdate):
    if not ObjectId.is_valid(class_id):
        raise HTTPException(
            status_code=400,
            detail="Id not found"
        )
    


    update_data=scholl_class.model_dump(exclude_unset=True)

    if update_data is None:
        raise HTTPException(
            status_code=404,
            detail="Class not found"
        )

    result = classes_collection.update_one(
        {"_id":ObjectId(class_id)},
        {"$set":update_data}
    )

    return{"message":"Update Successfully"}


@app.delete("/class/{class_id}")
def delete_class(class_id:str):
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



