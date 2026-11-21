from app.database import client
from app.database import db, student_collection
try:
    client.admin.command("ping")
    print("MongoDB Connected Successfully!")

except Exception as e:
    print("Connection failed:", e)
print("Database:", db.name)
print("Students Count:", student_collection.count_documents({}))