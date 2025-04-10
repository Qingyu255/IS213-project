"use client"
import { useEffect, useState } from "react"
import { useSearchParams, useRouter } from "next/navigation"
import { ErrorMessageCallout } from "@/components/error-message-callout"
import { EventList } from "./components/event-list"
import { Pagination } from "@/components/pagination"
import { Badge } from "@/components/ui/badge"
// import { BrowseByCategory } from "./components/browse-by-category";
// import { BrowseByLocation } from "./components/browse-by-location";
import { Separator } from "@/components/ui/separator"
import { BACKEND_ROUTES } from "@/constants/backend-routes"
import { EventDetails } from "@/types/event"
import EventsLoading from "./components/EventsLoading"
import { getAvailableTickets } from "@/lib/api/tickets"

// Add ticket info to event type
type EventWithTickets = EventDetails & {
  ticketInfo?: {
    availableTickets: number
    totalCapacity: number
    bookedTickets: number
  }
}

type EventsData = {
  events: EventWithTickets[]
}

async function getEvents(page = 1, limit = 9): Promise<EventsData> {
  const skip = (page - 1) * limit
  const res = await fetch(
    `${BACKEND_ROUTES.eventsService}/api/v1/events/?skip=${skip}&limit=${limit}`,
    {
      headers: {
        Accept: "application/json",
      },
    }
  )

  if (!res.ok) {
    throw new Error(`Failed to fetch events: ${res.statusText}`)
  }

  const data = (await res.json()) as EventDetails[]
  return { events: data }
}

export default function EventsPage() {
  const searchParams = useSearchParams()
  const router = useRouter()

  // If no page param is present, redirect to ?page=1
  const pageParam = searchParams.get("page")
  useEffect(() => {
    if (!pageParam) {
      router.push("?page=1")
    }
  }, [pageParam, router])

  // Use the page param from search params or default to 1
  const [page, setPage] = useState(pageParam ? Number(pageParam) : 1)
  const limit = 9
  const [eventsData, setEventsData] = useState<EventsData | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    async function fetchEvents() {
      try {
        const data = await getEvents(page, limit)

        // Fetch ticket info for each event
        const eventsWithTickets = await Promise.all(
          data.events.map(async (event) => {
            try {
              const ticketInfo = await getAvailableTickets(event.id)
              return {
                ...event,
                ticketInfo: {
                  availableTickets:
                    (event.capacity ?? 0) === 0
                      ? "Unlimited"
                      : ticketInfo.available_tickets,
                  totalCapacity:
                    (event.capacity ?? 0) === 0
                      ? "Unlimited"
                      : event.capacity ?? 0,
                  bookedTickets:
                    (event.capacity ?? 0) === 0
                      ? 0
                      : (event.capacity ?? 0) - ticketInfo.available_tickets,
                },
              } as EventWithTickets
            } catch (error) {
              console.error(
                `Failed to fetch tickets for event ${event.id}:`,
                error
              )
              return event as EventWithTickets
            }
          })
        )

        setEventsData({ events: eventsWithTickets })
      } catch (err: any) {
        setError(err.message || "An unknown error occurred")
      } finally {
        setIsLoading(false)
      }
    }
    fetchEvents()
  }, [page, limit])

  function handlePageChange(newPage: number) {
    setPage(newPage)
    router.push(`?page=${newPage}`)
  }

  if (isLoading) {
    return <EventsLoading />
  }

  if (error) {
    return <ErrorMessageCallout errorMessage={error} />
  }

  if (!eventsData) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p>No events found.</p>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8 text-center">
          <Badge className="mb-4 bg-accent text-accent-foreground hover:bg-accent/80 border-0">
            Discover Amazing Events
          </Badge>
          <h1 className="py-3 text-4xl md:text-5xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-purple-400 via-cyan-400 to-blue-400">
            Upcoming Events
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Explore and join extraordinary events happening around you. From
            tech conferences to music festivals, find your next unforgettable
            experience.
          </p>
        </div>
        {/* <div className="flex flex-col md:flex-row gap-5">
          <BrowseByCategory />
          <BrowseByLocation />
        </div> */}
        <Separator className="my-4" />
        <EventList events={eventsData.events} />
        <Pagination
          hasMore={!(eventsData.events.length < limit)}
          limit={limit}
          currentPage={page}
          onPageChange={handlePageChange}
        />
      </div>
    </div>
  )
}
