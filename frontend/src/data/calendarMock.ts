/** Static events — replace with GET calendar_events / startup context when API is wired. */

export interface CalendarEvent {
  id: string
  title: string
  date: string
  type: 'deadline' | 'pre_bid' | 'document_due' | 'approval' | 'milestone'
  /** Optional workspace context (same shape as Tenderulkar; link removed in UI until routes exist). */
  caseId?: string
  caseName?: string
}

export const calendarEvents: CalendarEvent[] = [
  {
    id: 'EVT-001',
    title: 'Seed deck v3 — send to angels',
    date: '2026-04-15',
    type: 'deadline',
    caseName: 'Fundraising',
  },
  {
    id: 'EVT-002',
    title: 'Advisor call — GTM review',
    date: '2026-03-25',
    type: 'pre_bid',
    caseName: 'Product & GTM',
  },
  {
    id: 'EVT-003',
    title: 'Financial model — refresh in data room',
    date: '2026-03-25',
    type: 'document_due',
    caseName: 'Finance',
  },
  {
    id: 'EVT-004',
    title: 'Board slide pack — your approval',
    date: '2026-03-22',
    type: 'approval',
    caseName: 'Governance',
  },
  {
    id: 'EVT-005',
    title: 'INC-20A / compliance checkpoint',
    date: '2026-04-20',
    type: 'deadline',
    caseName: 'Legal',
  },
  {
    id: 'EVT-006',
    title: 'Pilot customer QBR',
    date: '2026-05-01',
    type: 'deadline',
    caseName: 'Revenue',
  },
  {
    id: 'EVT-007',
    title: 'Cap table update — new SAFE',
    date: '2026-03-28',
    type: 'document_due',
    caseName: 'Equity',
  },
  {
    id: 'EVT-008',
    title: 'Runway review with CFO advisor',
    date: '2026-05-10',
    type: 'deadline',
    caseName: 'Finance',
  },
  {
    id: 'EVT-009',
    title: 'Public beta launch milestone',
    date: '2026-04-05',
    type: 'milestone',
    caseName: 'Product',
  },
  {
    id: 'EVT-010',
    title: 'Accelerator application — last day',
    date: '2026-04-10',
    type: 'deadline',
  },
  {
    id: 'EVT-011',
    title: 'Team offsite planning call',
    date: '2026-04-01',
    type: 'pre_bid',
  },
  {
    id: 'EVT-012',
    title: 'Quarterly OKR close',
    date: '2026-04-01',
    type: 'milestone',
  },
]
