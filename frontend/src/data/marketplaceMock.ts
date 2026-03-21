/** Static TwinVerse / marketplace browse — replace with GET /api/v1/marketplace/twins when wired. */

export interface MarketplaceAgent {
  id: string
  name: string
  creatorHandle: string
  description: string
  /** Raw count for display formatting */
  interactionCount: number
  /** Optional gradient key for avatar fallback */
  avatarSeed: string
}

export interface MarketplaceSection {
  title: string
  agents: MarketplaceAgent[]
}

function agent(
  id: string,
  name: string,
  creatorHandle: string,
  description: string,
  interactionCount: number,
  avatarSeed: string,
): MarketplaceAgent {
  return { id, name, creatorHandle, description, interactionCount, avatarSeed }
}

export const marketplaceSections: MarketplaceSection[] = [
  {
    title: 'Popular',
    agents: [
      agent(
        '1',
        'Fundraising coach — Priya',
        'onlyfounders',
        'Practice your seed pitch, cap table questions, and investor objections in a safe sandbox.',
        312_800,
        'priya',
      ),
      agent(
        '2',
        'Legal basics for founders',
        'clara_ops',
        'NDAs, founder agreements, and incorporation FAQs explained without the jargon.',
        1_700_000,
        'clara',
      ),
      agent(
        '3',
        'Product roadmap critic',
        'buildfast',
        'Stress-test your roadmap: scope, milestones, and what to cut before your next release.',
        89_200,
        'roadmap',
      ),
      agent(
        '4',
        'Hiring — first 10 people',
        'people_lab',
        'Role scorecards, interview plans, and equity conversations for early-stage teams.',
        456_000,
        'hiring',
      ),
    ],
  },
  {
    title: 'Trending',
    agents: [
      agent(
        '5',
        'Cap table & ESOP explainer',
        'caplogic',
        'Model dilution, option pools, and common founder mistakes before you sign.',
        234_000,
        'cap',
      ),
      agent(
        '6',
        'GTM for B2B SaaS',
        'gtm_mira',
        'ICP, outbound sequences, and pilot-to-paid playbooks for Indian and global buyers.',
        178_500,
        'gtm',
      ),
      agent(
        '7',
        'Burn & runway sanity check',
        'finance_owl',
        'Translate your spreadsheet into weeks of runway and a simple board narrative.',
        92_100,
        'burn',
      ),
      agent(
        '8',
        'Deck teardown (10 slides)',
        'pitch_room',
        'Tighten problem, traction, and ask slides with investor-style feedback.',
        1_120_000,
        'deck',
      ),
    ],
  },
  {
    title: 'Try these',
    agents: [
      agent(
        '9',
        'Customer discovery interviewer',
        'ux_ravi',
        'Run a mock user interview and extract insights for your next experiment.',
        67_400,
        'ux',
      ),
      agent(
        '10',
        'Competitor scan (weekly)',
        'market_lens',
        'Structured view of positioning, pricing pages, and feature gaps vs your top rivals.',
        41_200,
        'comp',
      ),
      agent(
        '11',
        'Board memo writer',
        'board_bot',
        'Turn bullet updates into a clear monthly email for advisors and angels.',
        28_900,
        'board',
      ),
      agent(
        '12',
        'OnlyFounders Manager (preview)',
        'onlyfounders',
        'Workspace-aware assistant — tasks, docs, and fundraising prep in one thread.',
        12_400,
        'mgr',
      ),
    ],
  },
]
