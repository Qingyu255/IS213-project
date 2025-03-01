"use client"

import { useState } from "react"
import Image from "next/image"
import { Calendar, Clock, ChevronDown, Users, Pencil, Ticket, UserCheck } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Textarea } from "@/components/ui/textarea"

export default function CreateEventPage() {
  const [isUnlimited, setIsUnlimited] = useState(true)
  const [requireApproval, setRequireApproval] = useState(false)

  return (
    <div className="min-h-screen ">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto">
          <div className="mb-8 relative">
            <Image
              src="/placeholder.svg?height=200&width=200"
              alt="Abstract Event Image"
              width={200}
              height={200}
              className="rounded-lg"
            />
            <Button
              variant="outline"
              className="absolute bottom-2 right-2 bg-black/50 hover:bg-black/70  border-white/20"
            >
              Change Image
            </Button>
          </div>

          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <Select defaultValue="personal">
                <SelectTrigger className="w-[200px] bg-white/5  ">
                  <SelectValue placeholder="Select calendar" />
                </SelectTrigger>
                <SelectContent className="bg-gray-800 ">
                  <SelectItem value="personal">Personal Calendar</SelectItem>
                  <SelectItem value="work">Work Calendar</SelectItem>
                </SelectContent>
              </Select>

              <Select defaultValue="public">
                <SelectTrigger className="w-[150px] bg-white/5  ">
                  <SelectValue placeholder="Visibility" />
                </SelectTrigger>
                <SelectContent className="bg-gray-800 ">
                  <SelectItem value="public">Public</SelectItem>
                  <SelectItem value="private">Private</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <Input
              type="text"
              placeholder="Event Name"
              className="text-3xl font-bold bg-transparent placeholder-white/50"
            />

            <div className="relative">
              <Textarea
                placeholder="Add Description"
                className="w-full min-h-[100px] bg-white/5 rounded-md p-4  placeholder-white/50 focus:ring-1 focus:ring-purple-500"
              />
            </div>

            <div className="flex space-x-4">
              <div className="flex-1">
                <Label htmlFor="start-date" className="sr-only">
                  Start Date
                </Label>
                <div className="relative">
                  <Input id="start-date" type="date" className="bg-white/5  pl-10" />
                  <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 /50" />
                </div>
              </div>
              <div className="flex-1">
                <Label htmlFor="start-time" className="sr-only">
                  Start Time
                </Label>
                <div className="relative">
                  <Input id="start-time" type="time" className="bg-white/5   pl-10" />
                  <Clock className="absolute left-3 top-1/2 transform -translate-y-1/2 /50" />
                </div>
              </div>
            </div>

            <div className="flex space-x-4">
              <div className="flex-1">
                <Label htmlFor="end-date" className="sr-only">
                  End Date
                </Label>
                <div className="relative">
                  <Input id="end-date" type="date" className="bg-white/5   pl-10" />
                  <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 /50" />
                </div>
              </div>
              <div className="flex-1">
                <Label htmlFor="end-time" className="sr-only">
                  End Time
                </Label>
                <div className="relative">
                  <Input id="end-time" type="time" className="bg-white/5   pl-10" />
                  <Clock className="absolute left-3 top-1/2 transform -translate-y-1/2 /50" />
                </div>
              </div>
            </div>

            <Popover>
              <PopoverTrigger asChild>
                <Button
                  variant="outline"
                  className="w-full justify-between bg-white/5   hover:bg-white/10"
                >
                  GMT+00:00 UTC
                  <ChevronDown className="ml-2 h-4 w-4 opacity-50" />
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-full p-0 bg-gray-800 ">
                <div className="grid gap-4 p-4">
                  <div className="space-y-2">
                    <h4 className="font-medium leading-none">Timezone</h4>
                    <p className="text-sm /70">Set the timezone for your event.</p>
                  </div>
                  <Select defaultValue="utc">
                    <SelectTrigger className="w-full bg-white/5  ">
                      <SelectValue placeholder="Select timezone" />
                    </SelectTrigger>
                    <SelectContent className="bg-gray-800 ">
                      <SelectItem value="utc">GMT+00:00 UTC</SelectItem>
                      <SelectItem value="est">GMT-05:00 EST</SelectItem>
                      <SelectItem value="pst">GMT-08:00 PST</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </PopoverContent>
            </Popover>

            <Select defaultValue="minimal">
              <SelectTrigger className="w-full bg-white/5  ">
                <SelectValue placeholder="Select format" />
              </SelectTrigger>
              <SelectContent className="bg-gray-800 ">
                <SelectItem value="minimal">Minimal</SelectItem>
                <SelectItem value="standard">Standard</SelectItem>
                <SelectItem value="premium">Premium</SelectItem>
              </SelectContent>
            </Select>

            <div className="space-y-4 mt-8">
              <h2 className="text-xl font-semibold">Event Options</h2>

              <div className="space-y-4 backdrop-blur-md bg-white/5 border  rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Ticket className="h-5 w-5 /70" />
                    <span>Tickets</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="/70">Free</span>
                    <Button variant="ghost" size="icon" className="h-8 w-8 /70 hover:">
                      <Pencil className="h-4 w-4" />
                    </Button>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <UserCheck className="h-5 w-5 /70" />
                    <span>Require Approval</span>
                  </div>
                  <Switch checked={requireApproval} onCheckedChange={setRequireApproval} />
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Users className="h-5 w-5 /70" />
                    <span>Capacity</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="/70">Unlimited</span>
                    <Button variant="ghost" size="icon" className="h-8 w-8 /70 hover:">
                      <Pencil className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            </div>

            {!isUnlimited && (
              <div className="relative">
                <Input
                  type="number"
                  placeholder="Number of spots"
                  className="bg-white/5   pl-10"
                />
                <Users className="absolute left-3 top-1/2 transform -translate-y-1/2 /50" />
              </div>
            )}

            <Button className="w-full bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600  border-0">
              Create Event
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
