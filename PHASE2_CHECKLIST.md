# Phase 2 Completion Checklist

Before moving to Phase 3, verify everything below is working.

## ✅ Backend (FastAPI)

- [ ] All CRUD endpoints responding:
  - [ ] GET /api/{user_id}/tasks
  - [ ] POST /api/{user_id}/tasks
  - [ ] GET /api/{user_id}/tasks/{id}
  - [ ] PUT /api/{user_id}/tasks/{id}
  - [ ] DELETE /api/{user_id}/tasks/{id}
  - [ ] PATCH /api/{user_id}/tasks/{id}/complete

- [ ] Database Integration:
  - [ ] Neon PostgreSQL connected
  - [ ] SQLModel ORM working
  - [ ] Data persisting correctly

- [ ] Better Auth:
  - [ ] JWT tokens generated on login
  - [ ] JWT verification middleware working
  - [ ] User ID extracted from token
  - [ ] User isolation enforced

## ✅ Frontend (Next.js)

- [ ] Authentication:
  - [ ] Signup page working
  - [ ] Login page working
  - [ ] JWT token stored (cookies/localStorage)
  - [ ] Token sent with API requests (Authorization header)

- [ ] Task Management UI:
  - [ ] Task list displays
  - [ ] Can add new task
  - [ ] Can edit task
  - [ ] Can delete task
  - [ ] Can mark complete/incomplete
  - [ ] Only user's own tasks shown

## ✅ Deployment

- [ ] Frontend deployed to Vercel
- [ ] Backend deployed (Railway/Render/similar)
- [ ] Environment variables configured
- [ ] CORS configured correctly
- [ ] Production URLs accessible

## 🧪 Testing Scenarios

Test these end-to-end:

1. **User A Flow**:
   - [ ] Sign up
   - [ ] Log in
   - [ ] Add 3 tasks
   - [ ] Mark 1 complete
   - [ ] Delete 1 task
   - [ ] See 2 tasks remaining

2. **User B Flow**:
   - [ ] Sign up (different user)
   - [ ] Log in
   - [ ] Add 2 tasks
   - [ ] **VERIFY**: Don't see User A's tasks
   - [ ] Log out

3. **User A Returns**:
   - [ ] Log back in
   - [ ] **VERIFY**: Still see original 2 tasks
   - [ ] **VERIFY**: Don't see User B's tasks

## 🐛 Common Issues to Check

- [ ] No CORS errors in browser console
- [ ] JWT token not expired
- [ ] Database connection stable
- [ ] API responses have correct user_id filtering
- [ ] Network errors handled gracefully

## 📝 Documentation

- [ ] README.md updated with:
  - [ ] Setup instructions
  - [ ] Environment variables needed
  - [ ] Deployment URLs
  - [ ] Phase 2 features list

## 🚀 When All Checked

You're ready for Phase 3!

**Next Steps**:
1. Read: `docs/phase-guides/phase3-mcp-complete-guide.md`
2. Run: `python scripts/tools/init_mcp_server.py ./backend/mcp_server`
3. Test: `python scripts/tools/test_mcp_connection.py`

---

**Phase 2 Submission**:
- [ ] GitHub repo updated
- [ ] Demo video recorded (<90 seconds)
- [ ] Vercel URL shared
- [ ] Backend URL shared
