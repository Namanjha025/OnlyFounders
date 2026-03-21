import type { LucideIcon } from 'lucide-react'
import { FileCheck, Landmark } from 'lucide-react'

export type ServiceId = 'funding' | 'registration'

export const SERVICE_IDS: ServiceId[] = ['funding', 'registration']

export function isServiceId(value: string): value is ServiceId {
  return value === 'funding' || value === 'registration'
}

export interface ServiceAssistantConfig {
  title: string
  description: string
  icon: LucideIcon
  welcome: string
  suggestions: string[]
}

export const SERVICE_CONFIG: Record<ServiceId, ServiceAssistantConfig> = {
  funding: {
    title: 'Government startup funding',
    description: 'Schemes, eligibility, DPIIT, grants & credit-linked programs',
    icon: Landmark,
    welcome: `I'm your assistant for **startup funding from government organisations** in India.

I can help you with:
- **Central & state schemes** (Startup India, SIDBI, NIDHI, state startup policies)
- **Eligibility** (DPIIT recognition, MSME / Udyam, sector caps, turnover tests)
- **Where to apply** (portals, nodal agencies, required documents)
- **Timelines** and how to prepare a strong application

What stage is your startup at, and what kind of support are you looking for — grant, loan, or tax benefit?`,
    suggestions: [
      'What central schemes apply to a DPIIT-registered startup?',
      'How do I get Startup India recognition?',
      'Compare state vs central funding options',
      'List documents usually needed for a government grant application',
    ],
  },
  registration: {
    title: 'Company registration helper',
    description: 'Pvt Ltd, LLP, OPC — steps, MCA, name approval, compliance basics',
    icon: FileCheck,
    welcome: `I'm your assistant for **company registration** in India.

I can walk you through:
- **Choosing a structure** (Pvt Ltd, LLP, OPC, partnership)
- **MCA SPICe+** flow, name reservation, DIN, and digital signatures
- **Post-incorporation** (PAN, TAN, bank account, GST if applicable)
- **Founder obligations** (ROC filings, AGM, statutory registers)

Tell me whether you're **pre-incorporation** or already have a name in mind, and which state you're targeting.`,
    suggestions: [
      'Pvt Ltd vs LLP for a two-founder SaaS startup',
      'Step-by-step SPICe+ overview for a private limited company',
      'What is AGILE-PRO and when do I need it?',
      'After incorporation, what do I file in the first 30 days?',
    ],
  },
}

export function getReply(msg: string, service: ServiceId): string {
  const lower = msg.toLowerCase()

  if (service === 'funding') {
    if (lower.includes('dpiit') || lower.includes('startup india') || lower.includes('recognition')) {
      return `**Startup India / DPIIT recognition** is often the gateway to many central and state benefits.\n\n**Typical steps:**\n1. Incorporate your entity (Pvt Ltd / LLP / OPC).\n2. Register on the **Startup India hub** and submit the recognition form with your pitch deck, website, and supporting docs.\n3. DPIIT issues a certificate with a unique ID — keep it handy for banks and scheme portals.\n\n**Tips:** align your product with "innovation / scalable model" language schemes expect; keep cap table and financials ready.\n\nWant a checklist tailored to your sector (e.g. deeptech vs services)?`
    }
    if (lower.includes('scheme') || lower.includes('central') || lower.includes('state')) {
      return `**Central vs state funding** — both matter.\n\n**Central (examples):** credit guarantee schemes, R&D grants via nodal bodies, sector missions, sometimes **SIDBI / NABARD** windows for eligible startups.\n**State:** many states run **startup policies** with rent subsidies, patent reimbursements, or matching grants.\n\n**Practical approach:**\n1. Confirm **DPIIT / MSME** status.\n2. Check **your state's startup portal** and **Startup India** listings.\n3. Read the **eligibility PDF** for each scheme (sector, stage, ticket size).\n\nTell me your **state** and **stage** (idea / MVP / revenue) and I can narrow it down.`
    }
    if (lower.includes('document') || lower.includes('apply')) {
      return `**Documents** vary by scheme, but founders usually prepare:\n\n- Incorporation certificate, MOA/AOA or LLP agreement\n- DPIIT / Udyam certificate if applicable\n- Audited financials or CA-certified projections\n- KYC for directors, bank statements\n- Detailed **project note** (use of funds, milestones, impact)\n\n**Application tips:** mirror the scheme's evaluation criteria in your annexures; use clear milestones and a realistic utilization plan.\n\nIf you share whether you're applying for a **grant vs loan**, I can suggest a tighter doc list.`
    }
    return `Thanks — on **government startup funding**, here's a quick frame:\n\n1. **Map your stage** (pre-revenue, early revenue, growth).\n2. **Lock eligibility tags** (DPIIT, MSME, sector-specific).\n3. **Shortlist 2–3 schemes** and read their latest guidelines (not blog summaries).\n4. **Prepare one master data room** and adapt per form.\n\nYour message: "${msg.slice(0, 60)}${msg.length > 60 ? '…' : ''}"\n\nReply with **state + sector + funding type** (grant / loan / tax) and I'll suggest a sharper next step.`
  }

  if (lower.includes('llp') || lower.includes('private limited') || lower.includes('opc') || lower.includes('vs')) {
    return `**Pvt Ltd vs LLP vs OPC** (very short):\n\n- **Pvt Ltd:** investors prefer it; clear shareholding; more compliance (AGM, board minutes, ROC).\n- **LLP:** flexible for professional partnerships; less ideal if you plan **VC equity rounds** soon.\n- **OPC:** single founder; converts to Pvt Ltd if you add shareholders later.\n\nFor a **two-founder SaaS** aiming to raise equity, **Pvt Ltd** is the common default — but LLP can work if both partners want pass-through taxation and minimal equity complexity.\n\nWant a comparison focused on **funding readiness** or **tax / salary to founders**?`
  }
  if (lower.includes('spic') || lower.includes('mca') || lower.includes('step')) {
    return `**SPICe+ (MCA)** — high-level flow:\n\n1. **DSC** for directors (Class 2/3 as applicable).\n2. **Name reservation** (RUN / Part of SPICe+).\n3. **SPICe+ form:** capital, subscribers, registered office, director details.\n4. **AGILE-PRO** linked steps for GST / EPFO / ESIC where opted.\n5. **Pay stamp duty & fees**; on approval, you get **COI, PAN, TAN**.\n\nThen: open a bank account, issue shares, maintain **statutory registers**, and plan **first board meeting** minutes.\n\nTell me if you're stuck on **name approval** or **subscriber sheet** and I'll go deeper.`
  }
  if (lower.includes('agile')) {
    return `**AGILE-PRO** is bundled with SPICe+ to optionally apply for:\n- **GSTIN** (if you need it from day one)\n- **EPFO / ESIC** registrations for employees\n\nYou can skip parts that don't apply; many startups add GST later when turnover crosses thresholds — but banks and some B2B customers may ask for GST early.\n\nIf you describe **B2B vs B2C** and **expected revenue in 6 months**, I can suggest whether to tick GST in the first filing.`
  }
  if (lower.includes('30 days') || lower.includes('after incorporation') || lower.includes('first')) {
    return `**After incorporation — common early tasks:**\n\n- **Board meeting:** appoint first auditors (if applicable), authorize signatories, adopt registers.\n- **Issue share certificates** and update **SH-1**.\n- **PAN/TAN** are usually auto-generated; verify on IT portal.\n- **Bank account** in company name with COI + resolution.\n- Watch **Form INC-20A** (commencement) if your company type requires it before operations.\n\nExact filings depend on your **company type** and **date of incorporation** — always confirm on **MCA V3** notices.\n\nWhat incorporation date are you targeting?`
  }
  return `On **company registration**, I can go step-by-step for **SPICe+**, name rules, or post-incorporation compliance.\n\nYou asked: "${msg.slice(0, 60)}${msg.length > 60 ? '…' : ''}"\n\nShare **entity type you're leaning toward** and **which state** your registered office will be in, and I'll tailor the checklist.`
}
