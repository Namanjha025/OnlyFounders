# User Signup & Signin

**Module:** Auth
**Status:** Built

## Overview

Simple user registration and login. A user signs up with email, name, and password. No role is assigned at signup — they're just a platform user. They can explore the platform and later create a startup workspace or get invited to one.

## User Journey

1. User visits OnlyFounders
2. User signs up with email, first name, last name, password
3. User is now a platform user — no role, no startup
4. User can log in with email + password and receive a JWT token
5. User can explore the platform, browse, etc.
6. Later, they either create a workspace (become a founder) or get invited to one

## Technical Details

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/auth/register` | Create account (email, name, password) |
| POST | `/api/v1/auth/login` | Log in, receive JWT token |
| GET | `/api/v1/auth/me` | Get current user profile |

### User Table Fields

| Field | Required | Notes |
|-------|----------|-------|
| `email` | Yes | Unique, used for login |
| `first_name` | Yes | |
| `last_name` | Yes | |
| `hashed_password` | Yes | bcrypt hashed |
| `role` | Auto | Defaults to `founder` (to be revisited — should be no role) |
| `is_active` | Auto | Defaults to `true` |

### Auth Mechanism

- JWT-based stateless auth
- Token issued on login, included in `Authorization: Bearer` header
- Token expiry configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`

## Acceptance Criteria

- User can register with email, first name, last name, password
- Duplicate emails are rejected
- User can log in and receive a JWT token
- Authenticated user can fetch their own profile via `/me`
- Invalid credentials return 401

## Pending / Future

- No role assigned at signup (currently defaults to `founder` — needs update)
- OAuth / social login (Google, GitHub)
- Email verification
- Password reset flow
- Rate limiting on auth endpoints
