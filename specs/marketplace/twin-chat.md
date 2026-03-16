# Twin Chat

**Module:** Marketplace (TwinVerse)
**Status:** Not Started

## Overview

Users can chat with any Twin on the marketplace. The Twin acts as a receptionist — it answers questions about its creator, explains their services, helps book calls via Calendly, and guides the user. The Twin only knows what's in its own profile data — fully sandboxed.

## User Journey

1. User finds a Twin on the marketplace
2. Clicks "Chat with Twin"
3. Twin greets them: "Hi, I'm Sarah's AI Twin. She's an angel investor focused on early-stage fintech. How can I help?"
4. User asks questions: "What kind of startups does Sarah invest in?"
5. Twin answers based on its profile data
6. User says: "I'd like to book a call"
7. Twin provides the Calendly link: "Here's Sarah's booking link — [calendly.com/sarah]"
8. Conversation is saved — the Twin's owner can review conversations later

## Technical Details

### How the Twin AI Works

On every message:
1. Load the Twin's profile data (title, bio, about, services, memory, documents)
2. Build a system prompt:
   ```
   You are the AI Twin of {display_name}.
   Title: {title}
   About: {about}
   Services: {services}
   Calendly: {calendly_url}

   You ONLY know what's in this profile. Do not make up information.
   You represent {display_name} on the TwinVerse marketplace.
   Help users understand who {display_name} is, what they offer, and how to connect with them.
   If someone wants to book a call, share the Calendly link.
   Be friendly, professional, and helpful.
   ```
3. Include conversation history for context
4. Send to LLM, get response
5. Save both messages

### Twin Messages Table

Separate from workspace messages. These are marketplace conversations.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `id` | UUID | Auto | Primary key |
| `twin_id` | UUID | Yes | FK to twins — which Twin |
| `user_id` | UUID | Yes | FK to users — who's chatting |
| `role` | enum | Yes | user, assistant |
| `content` | text | Yes | Message content |
| `created_at` | timestamp | Auto | |

### Endpoints

| Method | Path | Description | Who |
|--------|------|-------------|-----|
| POST | `/api/v1/marketplace/twins/{twin_id}/chat` | Send a message to a Twin | Any authenticated user |
| GET | `/api/v1/marketplace/twins/{twin_id}/chat` | Get conversation history with a Twin | The chatting user |
| GET | `/api/v1/twins/me/conversations` | List all conversations with my Twin | Twin owner |
| GET | `/api/v1/twins/me/conversations/{user_id}` | View a specific conversation | Twin owner |

### Privacy

- Twin only accesses its own profile data — nothing from workspaces
- Conversation history is per user-Twin pair
- Twin owner can review all conversations with their Twin
- Users can only see their own conversation with a Twin

## Acceptance Criteria

- Users can chat with any active Twin on the marketplace
- Twin responds based solely on its profile data
- Twin can share Calendly link for booking
- Conversations are saved and retrievable
- Twin owner can review all conversations with their Twin
- Twin does not hallucinate info outside its profile
- Conversation history provides context for follow-up messages

## Pending / Future

- Twin owner gets notified of new conversations
- Twin can qualify leads ("What stage is your startup? What are you looking for?")
- Twin can collect info and send a summary to the owner
- Voice/video chat with Twins
- Twin personality customization (tone, communication style)
