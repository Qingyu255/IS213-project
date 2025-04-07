"use client";

import { EventDetails } from "@/types/event";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { HostingEventCard } from "./hosting-event-card";
import { useState } from "react";
import { toast } from "sonner";
import { useRouter } from "next/navigation";
import { Spinner } from "@/components/ui/spinner";
import { deleteEvent } from "@/lib/api/events";

interface HostingEventsProps {
  events: EventDetails[]
}

export function HostingEvents({ events }: HostingEventsProps) {
  const router = useRouter();
  const [hostingEvents, setHostingEvents] = useState<EventDetails[]>(events);
  const [isDeleting, setIsDeleting] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [eventToDelete, setEventToDelete] = useState<string | null>(null);

  const handleEditEvent = (eventId: string) => {
    router.push(`/my-events/edit/${eventId}`);
  };

  const openDeleteDialog = (eventId: string) => {
    setEventToDelete(eventId);
    setShowDeleteDialog(true);
  };

  const handleDeleteEvent = async () => {
    if (!eventToDelete) return;

    try {
      setIsDeleting(true);

      await deleteEvent(eventToDelete);

      // Remove the deleted event from state
      setHostingEvents((prev) =>
        prev.filter((event) => event.id !== eventToDelete)
      );
      toast.success("Event deleted successfully");
    } catch (error) {
      console.error("Error deleting event:", error);
      toast.error("Failed to delete event");
    } finally {
      setIsDeleting(false);
      setShowDeleteDialog(false);
      setEventToDelete(null);
    }
  };

  const closeDeleteDialog = () => {
    setShowDeleteDialog(false);
    setEventToDelete(null);
  };

  if (hostingEvents.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-muted-foreground mb-4">
          You are not hosting any events yet
        </p>
        <Button asChild>
          <Link href="/create">Create an Event</Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold">Events You&apos;re Hosting</h2>
        <Button asChild>
          <Link href="/create">Create New Event</Link>
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {hostingEvents.map((event) => (
          <HostingEventCard
            key={event.id}
            event={event}
            onEdit={handleEditEvent}
            onDelete={openDeleteDialog}
          />
        ))}
      </div>

      {/* Custom delete confirmation modal */}
      {showDeleteDialog && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-background rounded-lg shadow-lg max-w-md w-full mx-4 overflow-hidden">
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-2">Are you sure?</h3>
              <p className="text-muted-foreground mb-4">
                This action cannot be undone. This will permanently delete the
                event and any associated data.
              </p>

              <div className="flex justify-end space-x-2">
                <Button
                  variant="outline"
                  onClick={closeDeleteDialog}
                  disabled={isDeleting}
                >
                  Cancel
                </Button>
                <Button
                  variant="destructive"
                  onClick={handleDeleteEvent}
                  disabled={isDeleting}
                >
                  {isDeleting ? <Spinner className="mr-2" size="sm" /> : null}
                  Delete
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
