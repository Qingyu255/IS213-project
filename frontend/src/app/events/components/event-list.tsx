import { EventDetails } from "@/types/event";
import { EventCard } from "@/components/EventCard";

export function EventList({ events }: { events: EventDetails[] }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
      {events.map((event) => (
        <EventCard key={event.id} event={event} variant="default" />
      ))}
    </div>
  );
}
