# Learning Management System (LMS) - Agentic

A comprehensive Learning Management System built with Flask (backend) and React (frontend), featuring role-based access control, assignment management, attendance tracking, and an AI-powered chatbot assistant.

## 🚀 Features

### Core Features
- **Role-Based Access Control**: Three distinct user roles (Admin, Teacher, Student) with different permissions
- **User Management**: Create, update, and manage students, teachers, and admins
- **Course Management**: Create and manage courses, subjects, and sections
- **Assignment System**: Create assignments, submit work, and grade submissions
- **Attendance Tracking**: Mark and track student attendance
- **Results Management**: Record and manage student results
- **Announcements**: Post announcements to specific sections
- **Events**: Create and manage school events
- **Enrollment**: Enroll students in courses
- **AI Chatbot**: Intelligent assistant powered by LangGraph and Groq API

### User Roles

#### Admin
- Manage all users (students, teachers, admins)
- Create and manage sections
- Create and manage courses
- Create and manage subjects
- Manage enrollments
- View all system data

#### Teacher
- Create and manage assignments
- View and grade student submissions
- Mark attendance
- Record results
- Create announcements
- View assigned courses and subjects

#### Student
- View assigned courses and subjects
- View and submit assignments
- View attendance records
- View results
- View announcements
- Access AI chatbot

## 🛠️ Tech Stack

### Backend
- **Flask**: Python web framework
- **SQLAlchemy**: ORM for database operations
- **PyMySQL**: MySQL database connector
- **Flask-JWT-Extended**: JWT authentication
- **Flask-Bcrypt**: Password hashing
- **Marshmallow**: Data validation and serialization
- **Flask-CORS**: Cross-origin resource sharing
- **LangGraph**: AI agent framework
- **LangChain**: LLM integration
- **LangChain-Groq**: Groq API integration

### Frontend
- **React 18**: UI library
- **TypeScript**: Type-safe JavaScript
- **Vite**: Build tool and dev server
- **React Router DOM**: Client-side routing
- **Axios**: HTTP client
- **Tailwind CSS**: Utility-first CSS framework
- **Lucide React**: Icon library
- **React Hot Toast**: Toast notifications

### Database
- **MySQL**: Relational database

## 📁 Project Structure

```
LMS Agentic/
├── backend/
│   ├── app.py                 # Flask application entry point
│   ├── requirements.txt       # Python dependencies
│   └── src/
│       ├── __init__.py        # Flask app factory
│       ├── db.py              # Database configuration
│       ├── extention.py       # Flask extensions (JWT, Bcrypt)
│       ├── models/            # SQLAlchemy models
│       ├── routes/            # API route handlers
│       ├── schemas/           # Marshmallow schemas
│       ├── services/          # Business logic
│       └── agent/             # AI chatbot implementation
│
└── frontend/
    ├── package.json           # Node.js dependencies
    ├── vite.config.ts         # Vite configuration
    ├── tailwind.config.js     # Tailwind CSS configuration
    └── src/
        ├── main.tsx           # React entry point
        ├── App.tsx            # Main app component
        ├── components/        # Reusable components
        ├── contexts/          # React contexts
        ├── pages/             # Page components
        ├── services/          # API service layer
        ├── types/             # TypeScript type definitions
        └── utils/             # Utility functions
```

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+**
- **Node.js 16+** and **npm** or **yarn**
- **MySQL 5.7+** or **MariaDB 10.3+**
- **Git**

## 🔧 Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd "LMS Agentic"
```

### 2. Backend Setup

#### Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

#### Database Configuration

1. Create a MySQL database:
```sql
CREATE DATABASE llm_LMS;
```

2. Create a `.env` file in the `backend/` directory:
```env
# Database Configuration
DATABASE_URI=mysql+pymysql://username:password@localhost/llm_LMS

# JWT Configuration
JWT_SECRET_KEY=your-secret-key-here

# Flask Configuration
FLASK_DEBUG=True
PORT=5000

# Groq API (Optional - for chatbot)
GROQ_API_KEY=your-groq-api-key-here
```

**Note**: Replace `username` and `password` with your MySQL credentials.

#### Run Database Migrations

The database tables will be created automatically when you first run the application.

#### Start the Backend Server

```bash
python app.py
```

The backend will run on `http://localhost:5000`

### 3. Frontend Setup

#### Install Dependencies

```bash
cd frontend
npm install
```

#### Start the Development Server

```bash
npm run dev
```

The frontend will run on `http://localhost:5173` (or another port if 5173 is busy)

## 🌐 API Endpoints

The API is organized by resource. All endpoints are prefixed with `/api/`.

### Authentication
- `POST /api/login` - User login
- `POST /api/logout` - User logout (if implemented)

### Admin Endpoints
- `POST /api/add/admin` - Create admin
- `GET /api/get/admin` - Get admin(s)
- `PUT /api/update/admin` - Update admin
- `DELETE /api/delete/admin` - Delete admin

### Student Endpoints
- `POST /api/add/student` - Create student
- `GET /api/get/student` - Get student(s)
- `PUT /api/update/student` - Update student
- `DELETE /api/delete/student` - Delete student

### Teacher Endpoints
- `POST /api/add/teacher` - Create teacher
- `GET /api/get/teacher` - Get teacher(s)
- `PUT /api/update/teacher` - Update teacher
- `DELETE /api/delete/teacher` - Delete teacher

### Course Endpoints
- `POST /api/add/course` - Create course
- `GET /api/get/courses` - Get course(s)
- `PUT /api/update/course` - Update course
- `DELETE /api/delete/course` - Delete course

### Assignment Endpoints
- `POST /api/create/assignments` - Create assignment
- `GET /api/get/assignments` - Get assignment(s)
- `PUT /api/update/assignments/` - Update assignment
- `DELETE /api/delete/assignments/` - Delete assignment

### Submission Endpoints
- `POST /api/submit/assignment` - Submit assignment (Student only)
- `GET /api/get/submissions/by/student` - Get student submissions
- `GET /api/get/submissions/by/assignment` - Get assignment submissions
- `PUT /api/update/submission` - Update submission (Teacher only)
- `DELETE /api/delete/submission` - Delete submission

### Other Endpoints
- Sections, Subjects, Enrollments, Attendance, Results, Announcements, Events
- See `backend/API_DOCUMENTATION.md` for complete API documentation

**Note**: Most endpoints require JWT authentication. Include the token in the `Authorization` header:
```
Authorization: Bearer <your-jwt-token>
```

## 🔐 Authentication

The application uses JWT (JSON Web Tokens) for authentication:

1. Login with username and password
2. Receive a JWT token
3. Include the token in subsequent requests via the `Authorization` header
4. Tokens are stored in `localStorage` on the frontend

## 🎨 Frontend Features

- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Modern UI**: Built with Tailwind CSS for a clean, modern interface
- **Toast Notifications**: User-friendly feedback for actions
- **Protected Routes**: Role-based route protection
- **Error Handling**: Comprehensive error handling and user feedback
- **Type Safety**: Full TypeScript support

## 🤖 AI Chatbot

The system includes an AI-powered chatbot that provides role-specific assistance:

- **Admin Tools**: User management, course creation, system administration
- **Teacher Tools**: Assignment creation, grading, attendance tracking
- **Student Tools**: Assignment submission, course information, results viewing

The chatbot uses LangGraph for agent orchestration and Groq API for LLM inference.

**Note**: The chatbot requires a `GROQ_API_KEY` environment variable. The application will still run without it, but the chatbot feature will be unavailable.

## 🚦 Running the Application

### Development Mode

1. **Start the Backend**:
   ```bash
   cd backend
   python app.py
   ```

2. **Start the Frontend** (in a new terminal):
   ```bash
   cd frontend
   npm run dev
   ```

3. Open your browser and navigate to `http://localhost:5173`

### Production Build

#### Backend
The Flask app can be deployed using:
- Gunicorn
- uWSGI
- Docker
- Any WSGI-compatible server

#### Frontend
Build the frontend for production:

```bash
cd frontend
npm run build
```

The built files will be in the `dist/` directory.

## 🧪 Testing

### Backend Testing
```bash
cd backend
# Add your test commands here
```

### Frontend Testing
```bash
cd frontend
npm run lint
```

## 📝 Environment Variables

### Backend (.env)
```env
DATABASE_URI=mysql+pymysql://username:password@localhost/llm_LMS
JWT_SECRET_KEY=your-secret-key-here
FLASK_DEBUG=True
PORT=5000
GROQ_API_KEY=your-groq-api-key-here  # Optional
```

## 🐛 Troubleshooting

### Backend Issues

1. **Database Connection Error**:
   - Verify MySQL is running
   - Check database credentials in `.env`
   - Ensure the database exists

2. **Import Errors**:
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version (3.8+)

3. **Port Already in Use**:
   - Change the port in `.env` or `app.py`
   - Kill the process using the port

### Frontend Issues

1. **Cannot Connect to Backend**:
   - Verify backend is running on `http://localhost:5000`
   - Check CORS configuration
   - Verify API base URL in `frontend/src/services/api.ts`

2. **Build Errors**:
   - Clear `node_modules` and reinstall: `rm -rf node_modules && npm install`
   - Check Node.js version (16+)

## 📚 Additional Documentation

- Backend API Documentation: `backend/API_DOCUMENTATION.md`
- Frontend API Documentation: `frontend/API_DOCUMENTATION.md`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- Your Name - Initial work

## 🙏 Acknowledgments

- Flask community
- React community
- Tailwind CSS
- LangChain and LangGraph teams

## 📞 Support

For support, email your-email@example.com or create an issue in the repository.

---

**Note**: This is a development version. For production deployment, ensure proper security measures, environment variable management, and database backups.

