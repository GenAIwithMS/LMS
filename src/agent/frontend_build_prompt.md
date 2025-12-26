Frontend AI Agent Prompt — Build an LMS Frontend with Chatbot

Goal
- Create a minimal, production-minded frontend for the LMS backend in this repo, with an integrated chatbot UI that calls `/api/chat`.

Required tech stack (recommended)
- React + Vite (TypeScript optional)
- Styling: Tailwind CSS or MUI (pick one)
- HTTP: `axios`
- Routing: `react-router`
- Data fetching/cache: `@tanstack/react-query` (recommended)

High-level requirements
- Implement authentication flow
  - `POST /api/login` to obtain JWT. Store token securely (localStorage or cookie) and attach to `Authorization: Bearer <token>` for protected requests.
  - Redirect users based on `role` claim: `admin`, `teacher`, `student`.
- Scaffold main pages
  - Login page (public)
  - Dashboard (role-specific): show quick summaries and navigation
  - Courses / Subjects page
  - Assignments listing and create/edit (teacher role)
  - Student management (admin role)
  - Announcements, Events, Attendance, Results pages (basic CRUD views)
  - Enrollment / Sections pages
- Integrate Chatbot widget
  - Create a persistent Chatbot component available on all pages (collapsible drawer or bottom-right widget).
  - UI: messages list, input box, send button, typing indicator.
  - On send: POST `/api/chat` with `{ "message": "..." }`. Include JWT in header. Display assistant reply.
  - Show user role in the UI (from decoded JWT) and display role-based hint text.

API usage and mapping (examples)
- Login
  - `POST /api/login` body: `{ email, password }` → receives `token`.
- Chat
  - `POST /api/chat` body: `{ message }`. Response: `{ message: "...", status: "success", role: "<role>" }`.
- Assignments
  - Create: `POST /api/create/assignments` (teacher only)
  - Get: `GET /api/get/assignments` (query `?id=` optional)

Authentication implementation notes
- Decode JWT (client-side) to get `role` and user info. Use `jwt-decode` package or server-provided user details.
- All protected requests must set header `Authorization: Bearer <token>`.

UX details for Chatbot
- Persist conversation locally (in component state) while session active.
- Support quick tool suggestions returned by backend (if backend includes them in messages). If assistant includes structured JSON, render actionable buttons (e.g., `Create Assignment` shortcut).
- Gracefully handle 401/403 by redirecting to login and showing an explanatory message.

Dev tasks for the AI agent (deliverables)
1. Scaffold a Vite React app in a `frontend/` folder with the chosen styling system and essential dependencies.
2. Implement an `apiClient` module that centralizes `axios` instance and auth header injection.
3. Implement `AuthContext` (or similar) to manage token, user role, and login/logout.
4. Implement core pages: `Login`, `Dashboard`, `Assignments`, `Students`, `Courses`, `Announcements`, `Attendance`, `Results` (each with basic CRUD flows using the backend endpoints).
5. Implement `Chatbot` component and wire it into the app shell. Provide nice-to-have features: message timestamps, scroll-to-bottom, error states.
6. Provide `README.md` in the `frontend/` folder with install & run commands.

Commands the agent should output (example)
```bash
cd frontend
npm install
npm run dev
```

Acceptance criteria
- The frontend runs locally and can authenticate against the backend.
- The Chatbot widget sends messages to `/api/chat` and displays responses.
- Role-based views enforce who can access create/update/delete actions (client-side guards and backend will enforce server-side).

Extra credit (optional)
- Use React Query for caching and invalidation.
- Provide a set of reusable components: `DataTable`, `FormModal`, `ConfirmDialog`, `ChatMessage`.
- Add unit tests for `apiClient` and `Chatbot` component.

Notes for the agent
- Use the backend API documented in `src/API_DOCUMENTATION.md` and inspect `src/schemas` for exact field names where necessary.
- Keep the initial implementation focused and functional; polish later.
