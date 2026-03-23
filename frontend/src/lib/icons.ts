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
  Users,
  UserPlus,
  Shield,
  Code,
  Palette,
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
  Users,
  UserPlus,
  Shield,
  Code,
  Palette,
}

export function resolveIcon(name: string | null | undefined): LucideIcon {
  if (!name) return Folder
  return iconMap[name] ?? Folder
}
