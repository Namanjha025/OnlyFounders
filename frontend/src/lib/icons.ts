import {
  Bot,
  PenTool,
  Search,
  Share2,
  FileCheck,
  Scale,
  Landmark,
  BarChart3,
  Megaphone,
  TrendingUp,
  Briefcase,
  Folder,
  type LucideIcon,
} from 'lucide-react'

const iconMap: Record<string, LucideIcon> = {
  Bot,
  PenTool,
  Search,
  Share2,
  FileCheck,
  Scale,
  Landmark,
  BarChart3,
  Megaphone,
  TrendingUp,
  Briefcase,
  Folder,
}

export function resolveIcon(name: string | null | undefined): LucideIcon {
  if (!name) return Folder
  return iconMap[name] ?? Folder
}
