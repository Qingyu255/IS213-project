import Image from "next/image";
import { Calendar, Clock, MapPin, Users, Globe, Share2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Separator } from "@/components/ui/separator";
import { EventMap } from "./components/event-map";
import { EventDetails } from "@/types/event";

// In a real app, this would fetch from an API
async function getEventDetails(id: string): Promise<EventDetails> {
  return {
    id,
    title: "Paris Blockchain Week 2025",
    date: "April 8-10, 2025",
    time: "9:00 AM - 6:00 PM",
    location: "Palais Brongniart, Paris",
    address: "16 Place de la Bourse, 75002 Paris, France",
    coordinates: { lat: 48.8697, lng: 2.3422 },
    image: "/placeholder.svg?height=400&width=800",
    category: "Technology",
    price: "€250",
    description:
      "Explore Paris Blockchain Week side events from April 8-10, uniting tech innovators and enthusiasts to navigate the evolving landscapes of crypto, DeFi, and NFTs.",
    schedule: [
      {
        time: "9:00 AM",
        title: "Registration & Welcome Coffee",
      },
      {
        time: "10:00 AM",
        title: "Opening Keynote: The Future of Blockchain",
      },
      {
        time: "11:30 AM",
        title: "Panel Discussion: DeFi Innovations",
      },
      {
        time: "1:00 PM",
        title: "Networking Lunch",
      },
    ],
    organizer: {
      name: "Blockchain Events Co",
      image: "/placeholder.svg?height=100&width=100",
      description: "Leading blockchain event organizer in Europe",
    },
    attendees: Array.from({ length: 12 }, (_, i) => ({
      id: `user-${i}`,
      name: `User ${i}`,
      image: `/placeholder.svg?height=40&width=40&text=${i}`,
    })),
    totalAttendees: 157,
  };
}

export default async function EventPage({
  params,
}: {
  params: { id: string };
}) {
  const event = await getEventDetails(params.id);

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <div className="relative h-[300px] md:h-[400px] ">
        <Image
          src={event.image || "/placeholder.svg"}
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
                  {event.date}
                </div>
                <div className="flex items-center">
                  <Clock className="w-5 h-5 mr-2" />
                  {event.time}
                </div>
                <div className="flex items-center">
                  <MapPin className="w-5 h-5 mr-2" />
                  {event.location}
                </div>
              </div>
            </div>

            {/* About Section */}
            <div className="bg-card rounded-lg p-6 shadow-lg">
              <h2 className="text-2xl font-bold mb-4">About Event</h2>
              <p className="text-muted-foreground mb-6">{event.description}</p>
              <Image
                src="/placeholder.svg?height=400&width=800"
                alt="Event preview"
                width={800}
                height={400}
                className="rounded-lg"
              />
            </div>

            {/* Schedule Section */}
            <div className="bg-card rounded-lg p-6 shadow-lg">
              <h2 className="text-2xl font-bold mb-4">Schedule</h2>
              <div className="space-y-4">
                {event.schedule.map((item, index) => (
                  <div key={index} className="flex items-start">
                    <div className="bg-primary/10 rounded-full p-2 mr-4">
                      <Clock className="w-4 h-4 text-primary" />
                    </div>
                    <div>
                      <div className="font-medium">{item.time}</div>
                      <div className="text-muted-foreground">{item.title}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Location Section */}
            <div className="bg-card rounded-lg p-6 shadow-lg">
              <h2 className="text-2xl font-bold mb-4">Location</h2>
              <p className="text-muted-foreground mb-4">{event.address}</p>
              <div className="h-[300px] rounded-lg overflow-hidden">
                <EventMap
                  center={event.coordinates}
                  zoom={15}
                  marker={event.coordinates}
                />
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Registration Card */}
            <div className="bg-card rounded-lg p-6 shadow-lg sticky top-6">
              <div className="flex justify-between items-center mb-6">
                <div className="text-2xl font-bold">{event.price}</div>
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
                {/* <div className="flex -space-x-2">
                  {event.attendees.map((attendee) => (
                    <Avatar key={attendee.id} className="border-2 border-background">
                      <AvatarImage src={attendee.image} alt={attendee.name} />
                      <AvatarFallback>{attendee.name[0]}</AvatarFallback>
                    </Avatar>
                  ))}
                  {event.totalAttendees > event.attendees.length && (
                    <div className="flex items-center justify-center w-8 h-8 rounded-full bg-muted text-muted-foreground text-sm">
                      +{event.totalAttendees - event.attendees.length}
                    </div>
                  )}
                </div> */}
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
                    alt={event.organizer.name}
                  />
                  <AvatarFallback>{event.organizer.name[0]}</AvatarFallback>
                </Avatar>
                <div>
                  <div className="font-medium">{event.organizer.name}</div>
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
