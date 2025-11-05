========================================
        Something To-Do
   Multi-User Task Management System
========================================

🌍 ENGLISH – User Guide

========================================

🚀 What is “Something To-Do”?
----------------------------------------
A multi-user task management system for families or teams.
Every user has their own tasks and login.
Admins can manage users and unlock accounts.

🧩 Requirements
----------------------------------------
• Python 3.x installed
• Required modules:
    - sqlite3 (built-in)
    - bcrypt   (for password hashing → install: pip install bcrypt)

📦 Project Files
----------------------------------------
• main.py              → Starts the program
• db.py                → Database & table structure
• auth.py              → Login / registration / user state
• tasks.py             → Task functions
• categories.py        → Category functions
• admin.py             → Admin management
• profile.py           → User profile
• utils.py             → Helper functions (input/date)

🛠️ How to start the application
----------------------------------------
Windows:
> python main.py

Mac/Linux:
$ python3 main.py

🔐 User Management
----------------------------------------
• Each user logs in with alias + password  
• 3 failed attempts → account is locked  
• Admin can unlock the user  

👥 User Roles
----------------------------------------
User: Manage personal tasks  
Admin: Additionally manage users and reset passwords  

✅ Main Features / Main Menu
----------------------------------------
1 – Create task  
2 – Show tasks  
3 – Mark task as completed  
4 – Delete task  
5 – Update task  
6 – Create category  
7 – Show categories  
8 – Login / switch user  
9 – Logout  
10 – Register new user  
11 – Open profile menu  

👑 Admin Menu (Admins only)
----------------------------------------
A – Show user list  
B – Unlock user account  
C – Reset user password  

✅ Profile Menu
----------------------------------------
• Show profile information  
• Change alias  
• Change password  


========================================
✅ Enjoy staying organized! 😄
========================================