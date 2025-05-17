# Quiz Master - Interactive Quiz Application

![Quiz Master](https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQiZf9wIELg4j3KKZpofhu_wZXQ5XCd878MQg&s)

**Version:** 1.0.0  
**Last Updated:** 2025-03-11 12:15:49  
**Developed by:** 23f2003700

## 📋 Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [Database Structure](#database-structure)
- [Usage](#usage)
- [Project Structure](#project-structure)

## 🚀 Introduction

Quiz Master is a comprehensive web application designed for educational institutions, teachers, and students to create, manage, and participate in interactive quizzes. The platform provides robust functionality for administrators to organize content by subjects and chapters, while offering students an intuitive interface to test their knowledge and track their progress.

## ✨ Features

### Admin Features
- **Complete Content Management**
  - Create and manage subjects
  - Organize chapters within subjects
  - Design quizzes with customizable questions
  - Set time limits for quizzes

- **User Management**
  - View and edit user profiles
  - Activate/deactivate user accounts
  - Assign admin privileges

- **Analytics & Reporting**
  - View quiz attempt statistics
  - Analyze performance by subject
  - Export reports in various formats

### Student Features
- **Learning Resources**
  - Browse available subjects and chapters
  - Access quizzes organized by topic

- **Quiz Experience**
  - Take timed quizzes
  - Receive immediate feedback and results
  - Review correct answers

- **Progress Tracking**
  - View personal quiz history
  - Track performance over time
  - Compare scores across different subjects

## 💻 Technology Stack

- **Backend:** Python 3.9+ with Flask framework
- **Database:** SQLAlchemy ORM with SQLite
- **Frontend:** HTML5, CSS3, Bootstrap 5
- **Authentication:** Flask-Login
- **Forms:** Flask-WTF, WTForms

## ⚙️ Installation

### Prerequisites
- Python 3.9 or higher
- Git
- pip (Python package manager)

### Local Setup

### Method 1
1. **Clone the repository**
    ```sh
    git clone https://github.com/23f2003700/QUIZ-MASTER-APP.git
    cd QUIZ-MASTER-APP
        
2. **Create Virtual Environment** with Python 3.12/3.11 version
   
3. **Run** "app.py" on VS code

### Method 2

1. **Clone the repository**
    ```sh
    git clone https://github.com/23f2003700/QUIZ-MASTER-APP.git
    cd QUIZ-MASTER-APP
    ```

2. **Create and activate a virtual environment**
    ```sh
    # Windows
    python -m venv venv
    venv\Scripts\activate

    # macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Install dependencies**
    ```sh
    pip install -r requirements.txt
    ```



4. **Run the application**
    ```sh
    python app.py
    ```

5. **Access the application**

    Open your browser and navigate to: [http://127.0.0.1:5000](http://127.0.0.1:5000) (your local port)

6. **Default Admin Login**
    - Email: admin@example.com
    - Password: admin123

## ⚙️ Configuration

Configuration options are stored in `config.py` and include:

- `SECRET_KEY`: Used for securely signing session cookies
- `SQLALCHEMY_DATABASE_URI`: Database connection string
- `PERMANENT_SESSION_LIFETIME`: Session timeout duration
- `MAIL_SERVER`, `MAIL_PORT`, etc.: Email configuration (for future features)

## 🗄️ Database Structure

The application uses the following data models:

- **User:** Stores user accounts including admin and student profiles
- **Subject:** Contains high-level subject categories
- **Chapter:** Organizes content within subjects
- **Quiz:** Defines quiz parameters including time limits
- **Question:** Stores individual questions with options and correct answers
- **Score:** Records users' quiz attempts and results

## 📝 Usage

### Admin Dashboard

After logging in as an administrator:

- **Subject Management**
  - Create new subjects from the Subjects tab
  - Add descriptions to help students identify content
  - Edit or remove subjects as curriculum changes

- **Chapter Organization**
  - Add chapters to subjects
  - Structure learning material in logical progression

- **Quiz Creation**
  - Create quizzes with configurable parameters
  - Add multiple-choice questions with assigned point values
  - Set time limits appropriate to quiz difficulty

### Student Experience

As a student:

- **Registration and Login**
  - Create an account with your email
  - Fill in profile information

- **Browsing Content**
  - Navigate through available subjects
  - Select chapters of interest

- **Taking Quizzes**
  - Start quiz when ready
  - Answer questions within time limit
  - Submit answers for immediate feedback

- **Reviewing Progress**
  - View performance history
  - Track improvements over time

## 📁 Project Structure

```plaintext
QUIZ-MASTER-APP/
├── app.py                  # Application entry point
├── config.py               # Configuration settings
├── extensions.py           # Flask extensions
├── requirements.txt        # Dependencies list
├── models/                 # Database models
│   ├── user.py
│   ├── subject.py
│   ├── chapter.py
│   ├── quiz.py
│   ├── question.py
│   └── score.py
├── controllers/            # Route handlers
│   ├── auth_controller.py
│   ├── admin_controller.py
│   └── user_controller.py
├── forms/                  # Form definitions
│   ├── auth.py
│   └── admin.py
├── static/                 # Static assets
│   ├── css/
│   │   └── style.css
│   └── images/
│       └── quiz-animation.gif
├── templates/              # HTML templates
│   ├── index.html
│   ├── layout.html
│   ├── admin/
│   ├── user/
│   └── auth/
```

