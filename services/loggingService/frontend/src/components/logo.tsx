import { siteName } from '@/constants/common'
import { Ticket } from 'lucide-react'
import React from 'react'

export default function Logo() {
  return (
    <div className="flex items-center gap-2">
        <div className="w-10 h-10 rounded-full bg-gradient-to-r from-purple-500 to-blue-500 flex items-center justify-center">
            <Ticket className="w-5 h-5" />
        </div>
        <span className="text-xl font-bold tracking-tight">{siteName}</span>
    </div>
  )
}
