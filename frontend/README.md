# Learning Management System (LMS) Frontend

A modern, responsive frontend application for the Learning Management System built with React, TypeScript, and Tailwind CSS.

## Features

- **Role-Based Access Control**: Separate interfaces for Admin, Teacher, and Student roles
- **Authentication**: JWT-based authentication with protected routes
- **Admin Features**:
  - Manage Students, Teachers, Sections, Courses, Subjects
  - Manage Enrollments and Events
  - Full CRUD operations for all entities

- **Teacher Features**:
  - Create and manage Assignments
  - Mark and manage Attendance
  - Create and grade Results
  - Create Announcements
  - Review and grade Student Submissions

- **Student Features**:
  - View Assignments
  - Submit Assignments (text and file uploads)
  - View Results and Grades
  - View Attendance Records
  - View Announcements

- **Chatbot**: AI-powered assistant for role-specific help

## Tech Stack

- **React 18** with TypeScript
- **Vite** for fast development and building
- **React Router** for navigation
- **Axios** for API calls
- **Tailwind CSS** for styling
- **Lucide React** for icons
- **React Hot Toast** for notifications

## Prerequisites

- Node.js 18+ and npm/yarn
- Backend API running on `http://localhost:5000`

## Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`

## Building for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## Project Structure

```
src/
├── components/          # Reusable components
│   ├── Layout.tsx      # Main layout with sidebar
│   ├── Modal.tsx       # Modal component
│   └── ProtectedRoute.tsx  # Route protection
├── contexts/           # React contexts
│   └── AuthContext.tsx # Authentication context
├── pages/              # Page components
│   ├── admin/          # Admin pages
│   ├── teacher/        # Teacher pages
│   ├── student/        # Student pages
│   ├── Dashboard.tsx   # Dashboard
│   ├── Login.tsx        # Login page
│   └── Chatbot.tsx     # Chatbot page
├── services/           # API services
│   └── api.ts          # API client
├── types/              # TypeScript types
│   └── index.ts        # Type definitions
├── App.tsx             # Main app component
├── main.tsx            # Entry point
└── index.css           # Global styles
```

## API Configuration

The frontend is configured to connect to the backend API at `http://localhost:5000`. The API base URL can be modified in `src/services/api.ts`.

## Authentication

- Login credentials are stored in JWT tokens
- Tokens are stored in localStorage
- Protected routes automatically redirect to login if not authenticated
- Role-based access control is enforced at the route level

## Usage

1. **Login**: Use valid credentials (email and password) to log in
2. **Dashboard**: View overview and quick actions based on your role
3. **Navigation**: Use the sidebar to navigate between different sections
4. **CRUD Operations**: Create, read, update, and delete operations are available through modals and tables

## Environment Variables

The application uses the following default configuration:
- API Base URL: `http://localhost:5000`
- Frontend Port: `3000`

To change these, modify:
- `src/services/api.ts` for API URL
- `vite.config.ts` for frontend port

## Features in Detail

### Admin Dashboard
- Complete management of all system entities
- User management (Students, Teachers, Admins)
- Course and Subject management
- Enrollment management
- Event creation and management

### Teacher Dashboard
- Assignment creation and management
- Attendance marking
- Result entry and management
- Announcement creation
- Submission review and grading

### Student Dashboard
- Assignment viewing and submission
- Result viewing
- Attendance tracking
- Announcement viewing

## Responsive Design

The application is fully responsive and works on:
- Desktop (1920px+)
- Laptop (1024px+)
- Tablet (768px+)
- Mobile (320px+)

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Notes

- All API calls include JWT authentication automatically
- Error handling is implemented with toast notifications
- Loading states are shown during API calls
- Form validation is implemented on the frontend
- File uploads are supported for assignment submissions

## Support

For issues or questions, please refer to the API documentation or contact the development team.

