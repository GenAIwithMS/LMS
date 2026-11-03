# Learning Management System (LMS) Agentic

A modern, comprehensive Learning Management System built with Flask (backend) and React 18 + TypeScript (frontend), featuring role-based access control, assignment management, attendance tracking, and an AI-powered chatbot assistant with LangGraph.

## ✨ Key Highlights

- **Modern UI/UX**: Gradient-based design with smooth animations and responsive layouts
- **Unified Dashboard**: All users (Admin, Teacher, Student) land on a centralized dashboard after login
- **Static Navigation**: Fixed sidebar and navbar with scrollable content area for better UX
- **AI-Powered Assistant**: Built-in chatbot widget accessible from any page
- **Real-time Notifications**: Toast notifications and notification center
- **Expandable Features**: Interactive feature cards with detailed descriptions on homepage

## 🚀 Features

### UI/UX Features
- **Modern Homepage**: 
  - Gradient hero section with animated backgrounds
  - Expandable feature cards with detailed capability lists
  - Problem-solution narrative layout
  - Role-based feature showcase
  - Security highlights section
- **Unified Dashboard**: Single dashboard for all user roles with role-specific quick actions
- **Static Layout**: Fixed sidebar and navbar, scrollable content area only
- **Responsive Design**: Mobile-first approach with collapsible sidebar
- **Enhanced Visuals**: Gradient cards, hover animations, shadow effects
- **Toast Notifications**: Real-time user feedback
- **Notification Center**: Bell icon with dropdown for announcements and events

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
- **Flask**: Lightweight Python web framework
- **SQLAlchemy**: ORM for database operations with relationship mapping
- **PyMySQL**: MySQL database connector
- **Flask-JWT-Extended**: JWT-based authentication and authorization
- **Flask-Bcrypt**: Secure password hashing
- **Marshmallow**: Data validation, serialization, and deserialization
- **Flask-CORS**: Cross-origin resource sharing configuration
- **LangGraph**: State-based AI agent orchestration framework
- **LangChain**: LLM integration and prompt management
- **LangChain-Groq**: Groq API integration for fast LLM inference
- **python-dotenv**: Environment variable management

### Frontend
- **React 18**: Latest React with hooks and concurrent features
- **TypeScript**: Full type safety and better developer experience
- **Vite**: Lightning-fast build tool and HMR dev server
- **React Router DOM v6**: Modern client-side routing
- **Axios**: Promise-based HTTP client with interceptors
- **Tailwind CSS 3**: Utility-first CSS with custom design system
- **Lucide React**: Modern icon library (350+ icons)
- **React Hot Toast**: Beautiful toast notifications
- **React Markdown**: Markdown rendering for chatbot responses
- **Remark GFM**: GitHub Flavored Markdown support

### Database
- **MySQL**: Relational database

## 📁 Project Structure

```
LMS Agentic/
├── backend/
│   ├── app.py                 # Flask application entry point
│   ├── requirements.txt       # Python dependencies
│   ├── .env.example          # Environment variables template
│   └── src/
│       ├── __init__.py        # Flask app factory with CORS config
│       ├── db.py              # Database configuration
│       ├── extention.py       # Flask extensions (JWT, Bcrypt)
│       ├── models/            # SQLAlchemy models (14 models)
│       │   ├── admin.py
│       │   ├── student.py
│       │   ├── teacher.py
│       │   ├── course.py
│       │   ├── assignment.py
│       │   └── ... (9 more)
│       ├── routes/            # API route handlers (15 blueprints)
│       │   ├── auth.py
│       │   ├── admin.py
│       │   ├── student.py
│       │   ├── chatbot.py
│       │   └── ... (11 more)
│       ├── schemas/           # Marshmallow schemas for validation
│       ├── services/          # Business logic layer
│       └── agent/             # AI chatbot implementation
│           ├── main.py        # LangGraph agent workflow
│           ├── tools.py       # 26 AI tools for database operations
│           ├── tools_list.py  # Tool registry
│           └── prompts.py     # System and role-specific prompts
│
└── frontend/
    ├── package.json           # Node.js dependencies
    ├── vite.config.ts         # Vite configuration
    ├── tailwind.config.js     # Tailwind CSS with custom colors
    ├── tsconfig.json          # TypeScript configuration
    └── src/
        ├── main.tsx           # React entry point
        ├── App.tsx            # Main app with routing (20+ routes)
        ├── index.css          # Global styles with custom animations
        ├── components/        # Reusable components
        │   ├── Layout.tsx     # Main layout with sidebar & navbar
        │   ├── ProtectedRoute.tsx
        │   ├── ChatbotWidget.tsx
        │   └── ...
        ├── contexts/          # React contexts
        │   └── AuthContext.tsx
        ├── pages/             # Page components
        │   ├── Homepage.tsx   # Landing page with features
        │   ├── Login.tsx      # Authentication page
        │   ├── Dashboard.tsx  # Unified dashboard
        │   ├── admin/         # Admin pages (7 pages)
        │   ├── teacher/       # Teacher pages (5 pages)
        │   └── student/       # Student pages (4 pages)
        ├── services/          # API service layer
        │   └── api.ts         # Axios instance with interceptors
        ├── types/             # TypeScript type definitions
        │   └── index.ts
        └── utils/             # Utility functions
            ├── jwt.ts
            └── errorHandler.ts
```

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.13**
- **Node.js 16+** and **npm** or **yarn**
- **MySQL 5.7+** or **MariaDB 10.3+**
- **Git**

## 🔧 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/GenAIwithMS/LMS
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

2. Create a `.env` file in the `backend/` directory (copy `backend/.env.example`):
```env
# Database Configuration
DATABASE_URI=mysql+pymysql://username:password@localhost/llm_LMS

# At least 32 characters, or the server refuses to start. Generate one with:
#   python -c "import secrets; print(secrets.token_hex(32))"
JWT_SECRET_KEY=paste-the-generated-value-here

# A login lasts this many minutes, then the user must log in again
JWT_EXPIRES_MINUTES=30

# The frontend's address (only this website may call the API)
CORS_ORIGINS=http://localhost:3000

# Only True on your own computer, never on a server
FLASK_DEBUG=False
PORT=5000

# Groq API (for the chatbot)
GROQ_API_KEY=your-groq-api-key-here
```

**Note**: Replace `username` and `password` with your MySQL credentials.

#### Create or Update the Database Tables

Tables are managed with migrations (Flask-Migrate). Run these from the `backend/` folder.

**New, empty database:**
```bash
flask --app app db upgrade
```

**Existing database from before this update** (it already has the original tables):
```bash
flask --app app db stamp 0001     # once: "my database already has the original tables"
flask --app app db upgrade        # adds unique usernames/emails and the new chat and login tables
```
If two accounts share a username or email, the upgrade stops and lists them without
changing anything. Change the username or email of the extra account, then run the upgrade again.

**After changing a model later:**
```bash
flask --app app db migrate -m "describe the change"
flask --app app db upgrade
```

#### Create the Admin Account

The LMS has a single admin, created once from the terminal (after the tables exist). There is no sign-up page or API for admins.

```bash
python create_admin.py
```

It asks for the admin's name, email, username and password (typed hidden). The admin then adds teachers and students from the dashboard.

#### Start the Backend Server

```bash
python app.py
```

The backend will run on `http://localhost:5000`

On a real server use gunicorn instead of `python app.py`:
```bash
gunicorn -w 1 -b 0.0.0.0:5000 app:app
```
(With more than one worker, set `RATELIMIT_STORAGE_URI` to a Redis address so the workers share their rate-limit counts.)

#### Run the Tests

```bash
pytest tests -v
```
See `backend/tests/README.md`. The tests need no MySQL and no Groq key.

#### Logins and Security

- A login lasts 30 minutes (`JWT_EXPIRES_MINUTES`). The user is logged out the moment it ends.
- Closing the tab or the browser logs the user out. So does leaving for another website and coming back with the Back button. Refreshing the page keeps the user logged in.
- Each browser tab has its own login: opening the LMS in a new tab asks for the login again.
- Logging out also blocks the token on the server, so it can't be reused.
- Login is limited to 10 attempts a minute per address, and the chatbot to 20 messages a minute per user.

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
- `POST /api/logout` - Log out (also blocks the token on the server)
- `GET /api/account` - The logged-in user's own account details
- `PUT /api/account/username` - Change your own username
- `PUT /api/account/password` - Change your own password (needs the current password)

### Admin Endpoints
- The admin is created with `python create_admin.py`, not through the API
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

1. Login with Email and password
2. Receive a JWT token
3. Include the token in subsequent requests via the `Authorization` header
4. Tokens are stored in `localStorage` on the frontend

## 🎨 Frontend Features

- **Modern Design System**: 
  - Gradient backgrounds and cards
  - Custom animations (fade-in-up, shimmer, pulse)
  - Glassmorphism effects
  - Smooth hover transitions
- **Responsive Layout**: Works seamlessly on desktop, tablet, and mobile
- **Fixed Navigation**: Sidebar and navbar stay static while content scrolls
- **Unified Dashboard**: Single landing page for all user roles after login
- **Interactive Homepage**: Expandable feature cards with detailed information
- **Toast Notifications**: Instant user feedback for all actions
- **Notification Center**: Real-time announcements and events dropdown
- **Protected Routes**: Role-based route protection with automatic redirects
- **Error Handling**: Comprehensive error handling with user-friendly messages
- **Type Safety**: Full TypeScript coverage for better developer experience
- **Loading States**: Skeleton loaders and spinners for better UX
- **Form Validation**: Client-side validation before API calls

## 🤖 AI Chatbot

The system includes an intelligent AI-powered chatbot accessible from any page via a floating button:

### Features
- **Role-Aware Context**: Chatbot adapts responses based on user role
- **26 Database Tools**: Complete CRUD operations via natural language
- **LangGraph Workflow**: State-based agent with tool calling
- **Markdown Rendering**: Rich formatting for chatbot responses
- **Persistent Widget**: Accessible from any page without navigation
- **Conversation History**: Maintains context within session

### Capabilities by Role

#### Admin Tools
- User management (create, update, delete students/teachers)
- Course and subject creation
- Section and enrollment management
- Event creation and management
- System-wide data queries

#### Teacher Tools
- Assignment creation and management
- Submission grading and feedback
- Attendance marking and tracking
- Result recording
- Announcement posting

#### Student Tools
- Assignment submission
- Grade and attendance viewing
- Course information queries
- Announcement viewing
- Schedule information

### Technical Implementation
- **LangGraph**: Orchestrates agent workflow with state management
- **Groq API**: Fast LLM inference (llama-3.3-70b-versatile model)
- **Tool Binding**: 26 Python functions exposed as tools
- **Error Handling**: Graceful fallbacks and error messages

**Note**: Requires `GROQ_API_KEY` in environment variables. Application runs without it, but chatbot will be unavailable.

## 🚦 Running the Application

### Development Mode

1. **Start the Backend** (Terminal 1):
   ```bash
   cd backend
   python app.py
   ```
   Backend runs on `http://localhost:5000`

2. **Start the Frontend** (Terminal 2):
   ```bash
   cd frontend
   npm run dev
   ```
   Frontend runs on `http://localhost:5173`

3. **Access the Application**:
   - Open `http://localhost:5173` in your browser
   - Login redirects all users to `/dashboard`
   - Navigate using the fixed sidebar

### First-Time Setup

1. **Create Admin User** (via API or database):
   ```bash
   # Use API endpoint or insert directly into database
   # Default credentials should be created in database
   ```

2. **Login Flow**:
   - Visit homepage → Click "Get Started" or "Login"
   - Enter credentials
   - Automatically redirected to unified dashboard
   - Access role-specific features from sidebar

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
flask run --debug
```

### Frontend Testing
```bash
cd frontend
npm run dev
```

## 📝 Environment Variables

### Backend (.env)
```env
# Database Configuration
DATABASE_URI=mysql+pymysql://username:password@localhost/llm_LMS

# JWT Configuration
JWT_SECRET_KEY=your-secret-key-here-change-this-in-production

# Flask Configuration
FLASK_DEBUG=True
PORT=5000

# Groq API (Required for AI Chatbot)
GROQ_API_KEY=your-groq-api-key-here
```

### Frontend (No .env needed)
Frontend uses Vite's default configuration. API base URL is set in `src/services/api.ts`:
```typescript
const API_BASE_URL = 'http://localhost:5000/api';
```

## 🐛 Troubleshooting

### Backend Issues

1. **Database Connection Error**:
   - Verify MySQL is running
   - Check database credentials in `.env`
   - Ensure the database exists

2. **Import Errors**:
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version (3.13 recommended, 3.8+ minimum)
   - Install `python-dotenv` separately if needed: `pip install python-dotenv`

3. **Port Already in Use**:
   - Change the port in `.env` or `app.py`
   - Kill the process using the port

### Frontend Issues

1. **Cannot Connect to Backend**:
   - Verify backend is running on `http://localhost:5000`
   - Check CORS configuration in `backend/src/__init__.py`
   - Verify API base URL in `frontend/src/services/api.ts`
   - Ensure no proxy/firewall blocking localhost connections

2. **Build Errors**:
   - Clear `node_modules` and reinstall: `rm -rf node_modules package-lock.json && npm install`
   - Check Node.js version (16+ required, 18+ recommended)
   - Clear Vite cache: `rm -rf node_modules/.vite`

3. **Login Issues**:
   - Check browser console for errors
   - Verify JWT token is being stored in localStorage
   - Clear localStorage and try again: `localStorage.clear()`
   - Check Network tab for API response status

4. **Styling Issues**:
   - Ensure Tailwind CSS is properly configured
   - Check `index.css` is imported in `main.tsx`
   - Rebuild with `npm run build` and restart dev server

## 📚 Additional Documentation

- **Backend API Documentation**: `backend/API_DOCUMENTATION.md`
- **Frontend API Documentation**: `frontend/API_DOCUMENTATION.md`
- **AI Agent Prompts**: `backend/src/agent/prompts.py`
- **Database Models**: `backend/src/models/`

## 🔄 Recent Updates

### UI/UX Improvements
- ✅ Modern gradient-based design system
- ✅ Unified dashboard for all user roles
- ✅ Fixed sidebar and navbar with scrollable content
- ✅ Expandable feature cards on homepage
- ✅ Enhanced notification system
- ✅ Improved responsive design
- ✅ Custom animations and transitions

### Features Added
- ✅ AI chatbot widget with 26 database tools
- ✅ Role-based dashboard quick actions
- ✅ Real-time notification center
- ✅ Toast notification system
- ✅ Markdown rendering for chatbot
- ✅ System status indicators (removed from dashboard)

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

---

**Note**: This is a development version. For production deployment, ensure proper security measures, environment variable management, and database backups.

