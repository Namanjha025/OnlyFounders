# Document Management

**Module:** Workspace
**Status:** Backend endpoints built

## Overview

Upload and manage documents within the startup workspace. Two categories:

1. **Startup documents** — pitch decks, incorporation docs, financial statements, board resolutions
2. **Member documents** — offer letters, contracts, NDAs, tax forms tied to a specific team member

All files are stored in S3 with presigned URLs for secure upload and download.

## User Journey

### Startup Documents

1. Founder goes to "Documents" in the workspace
2. Clicks "Upload" and selects a file + category
3. System generates a presigned S3 upload URL
4. File uploads directly to S3
5. Founder confirms upload, metadata saved
6. Document appears in the workspace document list
7. Team members with access can download via presigned URL

### Member Documents

1. Founder goes to a team member's profile
2. Uploads a document specific to that member (offer letter, NDA, etc.)
3. Document linked to both the startup and the member
4. Member can view their own documents

## Technical Details

### Document Categories

Startup-level: `pitch_deck`, `cap_table`, `financials`, `incorporation`, `business_plan`, `term_sheet`, `safe_agreement`, `patent`, `contract`, `other`

Member-level: `offer_letter`, `contract`, `nda`, `policy_acknowledgement`, `review`, `tax_form`, `other`

### S3 Integration

- **Upload:** Request presigned PUT URL -> upload directly to S3 -> confirm upload -> save metadata
- **Download:** Request presigned GET URL -> download directly from S3
- Presigned URLs have short TTL (configurable, default 1 hour)

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/startups/{id}/documents` | List startup documents |
| POST | `/api/v1/startups/{id}/documents/upload-url` | Get presigned upload URL |
| POST | `/api/v1/startups/{id}/documents/confirm-upload` | Confirm upload, save metadata |
| POST | `/api/v1/startups/{id}/documents/download-url` | Get presigned download URL |
| DELETE | `/api/v1/startups/{id}/documents/{doc_id}` | Delete document |
| GET | `/api/v1/startups/{id}/member-documents` | List member documents |
| POST | `/api/v1/startups/{id}/member-documents/upload-url` | Get presigned upload URL |
| POST | `/api/v1/startups/{id}/member-documents/confirm-upload` | Confirm upload |
| POST | `/api/v1/startups/{id}/member-documents/download-url` | Get presigned download URL |
| DELETE | `/api/v1/startups/{id}/member-documents/{mdid}` | Delete member document |

## Acceptance Criteria

- Upload startup documents via presigned S3 URLs
- Upload member-specific documents
- Documents categorized by type
- Download via presigned URLs with short TTL
- Metadata tracked (name, type, size, category, uploader, date)
- Documents can be deleted by authorized users

## Pending / Future

- Document versioning
- Folder organization
- Document search
- AI-powered document analysis
- Document signing integration (DocuSign, etc.)
- Access control per document by role
