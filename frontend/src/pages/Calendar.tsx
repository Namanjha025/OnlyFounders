import { useState } from 'react'
import {
  AlertTriangle,
  CalendarDays,
  Flag,
  FileText,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  X,
} from 'lucide-react'
import { calendarEvents } from '@/data/calendarMock'
import { daysUntil, cn } from '@/lib/utils'

const eventTypeConfig: Record<string, { label: string; icon: typeof AlertTriangle; short: string }> = {
  deadline: { label: 'Deadline', icon: AlertTriangle, short: 'Deadline' },
  pre_bid: { label: 'Meeting / call', icon: CalendarDays, short: 'Meeting' },
  document_due: { label: 'Document due', icon: FileText, short: 'Doc' },
  approval: { label: 'Approval needed', icon: CheckCircle2, short: 'Approval' },
  milestone: { label: 'Milestone', icon: Flag, short: 'Milestone' },
}

const DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
const MONTHS = [
  'January',
  'February',
  'March',
  'April',
  'May',
  'June',
  'July',
  'August',
  'September',
  'October',
  'November',
  'December',
]

function getMonthDays(year: number, month: number) {
  const firstDay = new Date(year, month, 1)
  const lastDay = new Date(year, month + 1, 0)
  let startOffset = firstDay.getDay() - 1
  if (startOffset < 0) startOffset = 6

  const days: (Date | null)[] = []
  for (let i = 0; i < startOffset; i++) days.push(null)
  for (let d = 1; d <= lastDay.getDate(); d++) days.push(new Date(year, month, d))
  while (days.length % 7 !== 0) days.push(null)
  return days
}

function isSameDay(a: Date, b: Date) {
  return (
    a.getFullYear() === b.getFullYear() &&
    a.getMonth() === b.getMonth() &&
    a.getDate() === b.getDate()
  )
}

export function Calendar() {
  const today = new Date()
  const [currentMonth, setCurrentMonth] = useState(today.getMonth())
  const [currentYear, setCurrentYear] = useState(today.getFullYear())
  const [selectedDate, setSelectedDate] = useState<Date | null>(null)

  const days = getMonthDays(currentYear, currentMonth)

  const eventsForDate = (date: Date) =>
    calendarEvents.filter((e) => isSameDay(new Date(e.date), date))

  const selectedEvents = selectedDate ? eventsForDate(selectedDate) : []

  const prevMonth = () => {
    if (currentMonth === 0) {
      setCurrentMonth(11)
      setCurrentYear(currentYear - 1)
    } else setCurrentMonth(currentMonth - 1)
  }
  const nextMonth = () => {
    if (currentMonth === 11) {
      setCurrentMonth(0)
      setCurrentYear(currentYear + 1)
    } else setCurrentMonth(currentMonth + 1)
  }
  const goToday = () => {
    setCurrentMonth(today.getMonth())
    setCurrentYear(today.getFullYear())
    setSelectedDate(today)
  }

  const upcomingCount = calendarEvents.filter((e) => daysUntil(e.date) > 0 && daysUntil(e.date) <= 7).length

  return (
    <div className="animate-fade-in space-y-5">
      <div className="flex items-end justify-between">
        <div>
          <h1 className="text-3xl font-semibold text-foreground tracking-tight">Calendar</h1>
          <p className="text-[15px] text-muted-foreground mt-1">
            {calendarEvents.length} events · {upcomingCount} this week
          </p>
        </div>
      </div>

      <div className="flex gap-5">
        <div className={cn('min-w-0 transition-all duration-300', selectedDate ? 'flex-1' : 'w-full')}>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <h2 className="text-xl font-semibold text-foreground">
                {MONTHS[currentMonth]} {currentYear}
              </h2>
              <button
                type="button"
                onClick={goToday}
                className="text-[13px] font-medium text-muted-foreground hover:text-foreground px-2.5 py-1 rounded-lg hover:bg-white/[0.06] transition-colors"
              >
                Today
              </button>
            </div>
            <div className="flex items-center gap-1">
              <button type="button" onClick={prevMonth} className="p-2 rounded-lg hover:bg-white/[0.06] transition-colors">
                <ChevronLeft className="w-4 h-4 text-muted-foreground" />
              </button>
              <button type="button" onClick={nextMonth} className="p-2 rounded-lg hover:bg-white/[0.06] transition-colors">
                <ChevronRight className="w-4 h-4 text-muted-foreground" />
              </button>
            </div>
          </div>

          <div className="grid grid-cols-7 mb-1">
            {DAYS.map((d) => (
              <div
                key={d}
                className="text-center py-2 text-[12px] font-semibold text-muted-foreground uppercase tracking-wider"
              >
                {d}
              </div>
            ))}
          </div>

          <div className="grid grid-cols-7 border-t border-l border-white/[0.06]">
            {days.map((date, i) => {
              if (!date) {
                return <div key={i} className="border-r border-b border-white/[0.06] bg-white/[0.01] min-h-[90px]" />
              }

              const isToday = isSameDay(date, today)
              const isSelected = selectedDate && isSameDay(date, selectedDate)
              const dayEvents = eventsForDate(date)
              const isCurrentMonth = date.getMonth() === currentMonth

              return (
                <button
                  key={i}
                  type="button"
                  onClick={() => setSelectedDate(date)}
                  className={cn(
                    'border-r border-b border-white/[0.06] min-h-[90px] p-2 text-left transition-colors relative',
                    isSelected ? 'bg-white/[0.06]' : 'hover:bg-white/[0.03]',
                    !isCurrentMonth && 'opacity-40'
                  )}
                >
                  <span
                    className={cn(
                      'inline-flex items-center justify-center w-7 h-7 rounded-full text-[13px] font-medium',
                      isToday ? 'bg-white text-black font-bold' : 'text-foreground'
                    )}
                  >
                    {date.getDate()}
                  </span>

                  {dayEvents.length > 0 && (
                    <div className="mt-1 space-y-0.5">
                      {dayEvents.slice(0, 3).map((evt) => (
                        <div
                          key={evt.id}
                          className={cn(
                            'text-[11px] font-medium px-1.5 py-0.5 rounded truncate',
                            evt.type === 'deadline' ? 'bg-white/[0.10] text-white' : 'bg-white/[0.05] text-zinc-300'
                          )}
                        >
                          {evt.title.length > 20 ? evt.title.slice(0, 20) + '...' : evt.title}
                        </div>
                      ))}
                      {dayEvents.length > 3 && (
                        <p className="text-[10px] text-muted-foreground px-1.5">+{dayEvents.length - 3} more</p>
                      )}
                    </div>
                  )}
                </button>
              )
            })}
          </div>
        </div>

        {selectedDate && (
          <div className="w-[340px] shrink-0 animate-slide-in">
            <div className="bg-card border border-white/[0.08] rounded-xl sticky top-0 overflow-hidden">
              <div className="flex items-center justify-between px-5 py-4 border-b border-white/[0.06]">
                <div>
                  <p className="text-[15px] font-semibold text-foreground">
                    {selectedDate.toLocaleDateString('en-IN', {
                      weekday: 'long',
                      day: 'numeric',
                      month: 'long',
                    })}
                  </p>
                  <p className="text-[13px] text-muted-foreground mt-0.5">
                    {selectedEvents.length === 0
                      ? 'No events'
                      : `${selectedEvents.length} event${selectedEvents.length > 1 ? 's' : ''}`}
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => setSelectedDate(null)}
                  className="p-1.5 rounded-lg hover:bg-white/[0.06] transition-colors"
                >
                  <X className="w-4 h-4 text-muted-foreground hover:text-foreground" />
                </button>
              </div>
              <div className="p-4 space-y-3 max-h-[calc(100vh-320px)] overflow-y-auto">
                {selectedEvents.length === 0 ? (
                  <p className="text-[14px] text-muted-foreground text-center py-8">No events on this day</p>
                ) : (
                  selectedEvents.map((evt) => {
                    const config = eventTypeConfig[evt.type] || eventTypeConfig.milestone
                    const d = daysUntil(evt.date)
                    return (
                      <div key={evt.id} className="p-3.5 bg-white/[0.02] border border-white/[0.06] rounded-lg space-y-2">
                        <div className="flex items-start gap-3">
                          <div className="p-2 rounded-lg bg-white/[0.06] shrink-0 mt-0.5">
                            <config.icon className="w-4 h-4 text-zinc-400" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="text-[15px] font-medium text-foreground">{evt.title}</p>
                            <p className="text-[13px] text-muted-foreground mt-0.5">{config.label}</p>
                          </div>
                        </div>
                        <div className="flex items-center justify-between pl-11">
                          <span
                            className={cn(
                              'text-[13px] font-semibold',
                              d <= 3 ? 'text-white' : d <= 7 ? 'text-zinc-300' : 'text-muted-foreground'
                            )}
                          >
                            {d > 0 ? `${d} days away` : d === 0 ? 'Today' : 'Passed'}
                          </span>
                          {evt.caseName ? (
                            <span className="text-[13px] text-muted-foreground truncate max-w-[140px]">
                              {evt.caseName}
                            </span>
                          ) : null}
                        </div>
                      </div>
                    )
                  })
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
