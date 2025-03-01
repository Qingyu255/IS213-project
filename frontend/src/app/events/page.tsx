import { EventList } from "./components/event-list"
import { Pagination } from "@/components/pagination"
import { Badge } from "@/components/ui/badge"
import { BrowseByCategory } from "./components/browse-by-category"
import { BrowseByLocation } from "./components/browse-by-location"
import { Separator } from "@/components/ui/separator"

// type Event = {
//   id: string;
//   name: string;
//   image: string;
//   date: string;
//   location: string;
//   attendees: number;
//   category: string;
// };

async function getEvents(page = 1, limit = 9) {
  // Dummy data
  const allEvents = Array.from({ length: 50 }, (_, i) => ({
    id: `event-${i + 1}`,
    name: `Event ${i + 1}`,
    image: `/placeholder.svg?height=300&width=400&text=Event+${i + 1}`,
    date: new Date(Date.now() + Math.random() * 30 * 24 * 60 * 60 * 1000).toLocaleDateString(),
    location: ["San Francisco", "New York", "London", "Tokyo", "Berlin"][Math.floor(Math.random() * 5)],
    attendees: Math.floor(Math.random() * 1000) + 50,
    category: ["Technology", "Music", "Art", "Business", "Sports"][Math.floor(Math.random() * 5)],
  }))

  // Simulate API delay
  await new Promise((resolve) => setTimeout(resolve, 500))

  const start = (page - 1) * limit
  const end = start + limit
  const paginatedEvents = allEvents.slice(start, end)

  return {
    events: paginatedEvents,
    total: allEvents.length,
  }
}

export default async function EventsPage({
  searchParams,
}: {
  searchParams: { [key: string]: string | string[] | undefined }
}) {
  const page = typeof searchParams.page === "string" ? Number(searchParams.page) : 1
  const limit = 9
  const { events, total } = await getEvents(page, limit)

  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8 text-center">
          <Badge className="mb-4 bg-accent text-accent-foreground hover:bg-accent/80 border-0">
            Discover Amazing Events
          </Badge>
          <h1 className="text-4xl md:text-5xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-purple-400 via-cyan-400 to-blue-400">
            Upcoming Events
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Explore and join extraordinary events happening around you. From tech conferences to music festivals, find
            your next unforgettable experience.
          </p>
        </div>
        <div className="flex flex-col md:flex-row gap-5">
            <BrowseByCategory />
            <BrowseByLocation />
        </div>
        <Separator className="my-4"/>
        <EventList events={events} />
        <Pagination total={total} limit={limit} />
      </div>
    </div>
  )
}

