import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


app = FastAPI(
    title="Student Collaboration Hub",
    description="A platform for students to collaborate on projects and communicate.",
    version="1.0.0",
    openapi_tags=[
        {"name": "students", "description": "Student operations"},
        {"name": "projects", "description": "Project operations"},
        {"name": "messages", "description": "Messaging operations"}
    ]
)

# Enable CORS for all origins (for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# In-memory storage
students = []
projects = []
messages = []
comments = []
direct_messages = []

# Pydantic models
class StudentIn(BaseModel):
    name: str
    avatar: str = None

class ProjectIn(BaseModel):
    title: str
    description: str
    status: str = "In Progress"

class CommentIn(BaseModel):
    author: str
    content: str

class MessageIn(BaseModel):
    sender: str
    content: str

class DirectMessageIn(BaseModel):
    sender: str
    recipient: str
    content: str

# Helper: find student by name
def get_student_by_name(name):
    for s in students:
        if s["name"] == name:
            return s
    return None

@app.get("/", tags=["greetings"])
async def root():
    return {"message": "Welcome to the Student Collaboration Hub!"}


# Login (demo, no password)
@app.post("/login", tags=["students"])
async def login(username: str):
    # In a real app, check password, etc.
    return {"success": True, "username": username}



# Students
@app.post("/students", tags=["students"])
async def add_student(student: StudentIn):
    if get_student_by_name(student.name):
        return {"error": "Student already exists"}
    avatar_val = student.avatar if student.avatar else student.name[0].upper()
    s = {"id": len(students)+1, "name": student.name, "avatar": avatar_val, "projects": []}
    students.append(s)
    return s

@app.get("/students", tags=["students"])
async def list_students():
    return students

# Join project
@app.post("/projects/{project_id}/join", tags=["projects"])
async def join_project(project_id: int, student_name: str):
    student = get_student_by_name(student_name)
    if not student:
        return {"error": "Student not found"}
    for p in projects:
        if p["id"] == project_id:
            if student_name not in p.get("members", []):
                p.setdefault("members", []).append(student_name)
                student["projects"].append(project_id)
                return {"success": True, "project": p}
            else:
                return {"error": "Already a member"}
    return {"error": "Project not found"}

# Projects
@app.post("/projects", tags=["projects"])
async def add_project(project: ProjectIn):
    p = {"id": len(projects)+1, "title": project.title, "description": project.description, "status": project.status, "members": []}
    projects.append(p)
    return p

@app.get("/projects", tags=["projects"])
async def list_projects(status: str = None):
    if status:
        return [p for p in projects if p.get("status", "In Progress") == status]
    return projects

# Comments on projects
@app.post("/projects/{project_id}/comments", tags=["projects"])
async def add_comment(project_id: int, comment: CommentIn):
    c = {"id": len(comments)+1, "project_id": project_id, "author": comment.author, "content": comment.content}
    comments.append(c)
    return c

@app.get("/projects/{project_id}/comments", tags=["projects"])
async def get_comments(project_id: int):
    return [c for c in comments if c["project_id"] == project_id]

# Messages
@app.post("/messages", tags=["messages"])
async def post_message(message: MessageIn):
    m = {"id": len(messages)+1, "sender": message.sender, "content": message.content}
    messages.append(m)
    return m

@app.get("/messages", tags=["messages"])
async def list_messages():
    return messages

# Direct Messages
@app.post("/direct-messages", tags=["messages"])
async def send_dm(dm: DirectMessageIn):
    d = {"id": len(direct_messages)+1, "from": dm.sender, "to": dm.recipient, "content": dm.content}
    direct_messages.append(d)
    return d

@app.get("/direct-messages/{username}", tags=["messages"])
async def get_dms(username: str):
    return [dm for dm in direct_messages if dm["from"] == username or dm["to"] == username]
