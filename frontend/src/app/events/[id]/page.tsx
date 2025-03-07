"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import { Calendar, Clock, MapPin, Users, Globe, Share2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Separator } from "@/components/ui/separator";
import { EventMap } from "./components/event-map";
import { EventDetails } from "@/types/event";
import { BACKEND_ROUTES } from "@/constants/backend-routes";
import { InterestCategory } from "@/enums/InterestCategory";

type EventPageProps = {
  id: string;
};

export default function EventPage({ id }: EventPageProps) {
  const [event, setEvent] = useState<EventDetails | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch event details on component mount
  useEffect(() => {
    async function fetchEvent() {
      try {
        // const res = await fetch(
        //   `${BACKEND_ROUTES.createEventServiceUrl}/api/events/${id}`
        // );
        // if (!res.ok) {
        //   throw new Error(`Failed to fetch event details: ${res.status}`);
        // }
        // const data: EventDetails = await res.json();
        // setEvent(data);

        const dummyEventDetails: EventDetails = {
          id: "dummy-event-001",
          title: "Test Event: Innovation Summit 2025",
          description:
            "This is a dummy event used for testing. Join us for an innovative summit featuring thought leaders in technology and business.",
          startDateTime: "2025-05-15T09:00:00Z",
          endDateTime: "2025-05-15T17:00:00Z",
          venue: {
            address: "123 Test Street, Test City, TS 12345",
            name: "Test Venue",
            city: "Test City",
            state: "TS",
            additionalDetails: "Suite 100, Test Building",
            coordinates: { lat: 37.7749, lng: -122.4194 },
          },
          imageUrl: "/placeholder.svg",
          category: InterestCategory.Technology,
          price: {
            amount: 50,
            currency: "USD",
          },
          schedule: [
            {
              startTime: "09:00 AM",
              endTime: "10:00 AM",
              title: "Registration & Welcome Coffee",
              description: "Meet and greet with participants.",
            },
            {
              startTime: "10:00 AM",
              endTime: "11:30 AM",
              title: "Keynote: Future of Innovation",
              description: "An inspiring talk about the future of technology.",
            },
          ],
          organizer: {
            id: "organizer-001",
            username: "OrganizerUser",
          },
          attendees: [
            { id: "user-1", name: "Alice", imageUrl: "/alice.jpg" },
            { id: "user-2", name: "Bob", imageUrl: "/bob.jpg" },
          ],
          totalAttendees: 2,
          capacity: 100,
          eventType: "public",
          invitedEmails: [],
          createdAt: "2025-01-01T00:00:00Z",
          updatedAt: "2025-01-02T00:00:00Z",
        };
        setEvent(dummyEventDetails); // TODO use actual fetched data when backend done
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
      } catch (err: any) {
        setError(err.message || "An error occurred");
      } finally {
        setIsLoading(false);
      }
    }
    fetchEvent();
  }, [id]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p>Loading event details...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-red-500">Error: {error}</p>
      </div>
    );
  }

  if (!event) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p>No event found.</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <div className="relative h-[300px] md:h-[400px]">
        <Image
          src={event.imageUrl || "/placeholder.svg"}
          alt={event.title}
          fill
          className="object-cover opacity-90"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-background to-transparent" />
      </div>

      <div className="container mx-auto px-4 -mt-16 relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Event Header */}
            <div className="bg-card rounded-lg p-6 shadow-lg">
              <Badge className="mb-4 bg-primary/10 text-primary hover:bg-primary/20 border-0">
                {event.category}
              </Badge>
              <h1 className="text-4xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-blue-400">
                {event.title}
              </h1>
              <div className="flex flex-wrap gap-4 text-muted-foreground">
                <div className="flex items-center">
                  <Calendar className="w-5 h-5 mr-2" />
                  {new Date(event.startDateTime).toLocaleDateString()}
                </div>
                <div className="flex items-center">
                  <Clock className="w-5 h-5 mr-2" />
                  {event.endDateTime
                    ? new Date(event.endDateTime).toLocaleTimeString()
                    : "Ongoing"}
                </div>
                <div className="flex items-center">
                  <MapPin className="w-5 h-5 mr-2" />
                  {event.venue.address}
                </div>
              </div>
            </div>

            {/* About Section */}
            <div className="bg-card rounded-lg p-6 shadow-lg">
              <h2 className="text-2xl font-bold mb-4">About Event</h2>
              <p className="text-muted-foreground mb-6">{event.description}</p>
              <Image
                src={event.imageUrl || "/placeholder.svg?height=400&width=800"}
                alt="Event preview"
                width={800}
                height={400}
                className="rounded-lg"
              />
            </div>

            {/* Schedule Section */}
            {event.schedule && event.schedule.length > 0 && (
              <div className="bg-card rounded-lg p-6 shadow-lg">
                <h2 className="text-2xl font-bold mb-4">Schedule</h2>
                <div className="space-y-4">
                  {event.schedule.map((item, index) => (
                    <div key={index} className="flex items-start">
                      <div className="bg-primary/10 rounded-full p-2 mr-4">
                        <Clock className="w-4 h-4 text-primary" />
                      </div>
                      <div>
                        <div className="font-medium">{item.startTime}</div>
                        <div className="text-muted-foreground">
                          {item.title}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Location Section */}
            <div className="bg-card rounded-lg p-6 shadow-lg">
              <h2 className="text-2xl font-bold mb-4">Location</h2>
              <p className="text-muted-foreground mb-4">
                {event.venue.address}
              </p>
              <h3 className="text-base font-bold mb-2">Additional Details</h3>
              <p className="text-sm text-muted-foreground mb-4">
                {event.venue.additionalDetails}
              </p>
              <div className="h-[300px] rounded-lg overflow-hidden">
                <EventMap
                  center={event.venue.coordinates}
                  zoom={15}
                  marker={event.venue.coordinates}
                />
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Registration Card */}
            <div className="bg-card rounded-lg p-6 shadow-lg sticky top-6">
              <div className="flex justify-between items-center mb-6">
                <div className="text-2xl font-bold">
                  {event.price.amount > 0
                    ? `${event.price.amount} ${event.price.currency}`
                    : "Free"}
                </div>
                <Button className="bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600">
                  Register Now
                </Button>
              </div>
              <Separator className="my-4" />
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center text-muted-foreground">
                    <Users className="w-5 h-5 mr-2" />
                    <span>Attendees</span>
                  </div>
                  <span>{event.totalAttendees}</span>
                </div>
              </div>
              <Separator className="my-4" />
              <div className="space-y-4">
                <h3 className="font-medium">Share Event</h3>
                <div className="flex gap-2">
                  <Button variant="outline" size="icon">
                    <Globe className="w-4 h-4" />
                  </Button>
                  <Button variant="outline" size="icon">
                    <Share2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </div>

            {/* Organizer Card */}
            <div className="bg-card rounded-lg p-6 shadow-lg">
              <h3 className="font-bold mb-4">Organized by</h3>
              <div className="flex items-center gap-4">
                <Avatar className="w-12 h-12">
                  <AvatarImage
                    src={event.organizer.image}
                    alt={event.organizer.username}
                  />
                  <AvatarFallback>{event.organizer.username[0]}</AvatarFallback>
                </Avatar>
                <div>
                  <div className="font-medium">{event.organizer.username}</div>
                  <div className="text-sm text-muted-foreground">
                    {event.organizer.description}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
