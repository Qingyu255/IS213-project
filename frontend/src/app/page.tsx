"use client";
import Link from "next/link";
import Image from "next/image";
import { ChevronRight, PlusCircle, ArrowRight, BarChart } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Route } from "@/enums/Route";
import { BACKEND_ROUTES } from "@/constants/backend-routes";
import { EventDetails } from "@/types/event";
import { siteName } from "@/constants/common";
import Logo from "@/components/logo";
import { EventCard } from "@/components/EventCard";
import { getBearerIdToken } from "@/utils/auth";
import { useEffect, useState } from "react";

export default function EventPlatformPage() {
  const [featuredEvents, setFeaturedEvents] = useState<EventDetails[]>([]);
  useEffect(() => {
    const fetchFeaturedEvents = async () => {
      try {
        const res = await fetch(
          `http://localhost:8100/api/v1/events/?skip=0&limit=3`,
          {
            headers: {
              Accept: "application/json",
              Authorization: await getBearerIdToken(),
            },
            next: { revalidate: 3600 },
          }
        );

        if (!res.ok) {
          throw new Error(`Failed to fetch events: ${res.statusText}`);
        }

        const data = (await res.json()) as EventDetails[];
        setFeaturedEvents(data);
      } catch (error) {
        console.error("Error fetching featured events:", error);
      }
    };
    fetchFeaturedEvents();
  }, []);

  return (
    <div className="min-h-screen bg-white dark:bg-black overflow-hidden">
      {/* Background elements */}
      <div className="fixed inset-0 z-0">
        <div
          className="absolute top-0 left-0 w-full h-full 
                    bg-gradient-to-br 
                    from-purple-200/50 via-white to-blue-200/50
                    dark:from-purple-900/20 dark:via-black dark:to-blue-900/20"
        />
        <div
          className="absolute top-1/4 left-1/4 w-96 h-96 rounded-full 
                    bg-purple-300/20 dark:bg-purple-500/10 blur-3xl"
        />
        <div
          className="absolute bottom-1/3 right-1/4 w-64 h-64 rounded-full 
                    bg-blue-300/20 dark:bg-blue-500/10 blur-3xl"
        />
        <div
          className="absolute top-1/2 right-1/3 w-80 h-80 rounded-full 
                    bg-cyan-300/20 dark:bg-cyan-500/10 blur-3xl"
        />
      </div>

      {/* Hero Section */}
      <section className="relative z-10 py-10">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto text-center mb-12">
            <Badge className="mb-4 bg-white/10 hover:bg-white/20 text-black dark:text-white border-0">
              Reimagining Events
            </Badge>
            <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-purple-400 via-cyan-400 to-blue-400 leading-tight">
              Attend or Create Extraordinary Events
            </h1>
            <p className="text-lg md:text-xl /70 mb-8 max-w-3xl mx-auto">
              The all-in-one platform for discovering amazing events or creating
              your own with powerful tools designed for the modern creator.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href={Route.BrowseEvents}>
                <Button className="bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600  border-0 h-12 px-8 text-lg">
                  Find Events
                </Button>
              </Link>
              <Link href={Route.CreateEvent}>
                <Button
                  variant="outline"
                  className="border-white/20 h-12 px-8 text-lg"
                >
                  Create an Event
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Featured Events */}
      <section className="relative z-10 py-5">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-12">
            <div>
              <Badge className="mb-2 bg-white/10 hover:bg-white/20  border-0 text-black dark:text-white">
                Trending Now
              </Badge>
              <h2 className="text-3xl md:text-4xl font-bold">
                Featured Events
              </h2>
            </div>
            <div className="flex gap-4">
              <Link href={Route.BrowseEvents}>
                <Button variant="outline">
                  View All <ChevronRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {featuredEvents.length > 0 ? (
              featuredEvents.map((event) => (
                <EventCard
                  key={event.id}
                  event={event}
                  variant="featured"
                  showCapacity={true}
                  showTime={true}
                />
              ))
            ) : (
              <>
                {[1, 2, 3].map((placeholder) => (
                  <Card
                    key={placeholder}
                    className="bg-white/5 border-white/10 overflow-hidden"
                  >
                    <div className="relative">
                      <div className="w-full h-60 bg-gray-700/20 animate-pulse" />
                      <div className="absolute bottom-4 left-4 right-4">
                        <div className="h-6 w-3/4 bg-gray-700/20 animate-pulse rounded mb-2" />
                        <div className="h-4 w-1/2 bg-gray-700/20 animate-pulse rounded" />
                      </div>
                    </div>
                    <CardContent className="p-4">
                      <div className="space-y-3">
                        <div className="h-4 w-full bg-gray-700/20 animate-pulse rounded" />
                        <div className="h-4 w-3/4 bg-gray-700/20 animate-pulse rounded" />
                        <div className="h-4 w-1/2 bg-gray-700/20 animate-pulse rounded" />
                        <div className="pt-3 border-t border-white/10 flex justify-end">
                          <div className="h-9 w-28 bg-gray-700/20 animate-pulse rounded" />
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </>
            )}
          </div>
        </div>
      </section>

      {/* Create Events Section */}
      <section className="relative z-10 py-20 bg-gradient-to-b from-transparent to-purple-900/10">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <Badge className="mb-4 bg-white/10 hover:bg-white/20 border-0 text-black dark:text-white">
                For Event Creators
              </Badge>
              <h2 className="text-3xl md:text-5xl font-bold mb-6 leading-tight">
                Create Stunning Events in Minutes
              </h2>
              <p className="/70 text-lg mb-8">
                Our powerful yet simple tools make it easy to create, manage,
                and promote your events. From registration to analytics,
                we&apos;ve got you covered.
              </p>

              <div className="space-y-6">
                {[
                  {
                    icon: <PlusCircle className="h-6 w-6 text-purple-400" />,
                    title: "Easy Event Creation",
                    description:
                      "Intuitive tools to create beautiful event pages in minutes.",
                  },
                  {
                    icon: <BarChart className="h-6 w-6 text-cyan-400" />,
                    title: "Powerful Analytics",
                    description:
                      "Get real-time insights into attendance, engagement, and revenue.",
                  },
                ].map((feature, index) => (
                  <div key={index} className="flex gap-4">
                    <div className="flex-shrink-0 w-12 h-12 rounded-full bg-white/5 flex items-center justify-center">
                      {feature.icon}
                    </div>
                    <div>
                      <h3 className="font-bold text-lg">{feature.title}</h3>
                      <p className="text-muted-foreground">
                        {feature.description}
                      </p>
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-8">
                <Link href={Route.CreateEvent}>
                  <Button className="bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600 border-0 h-12 px-8">
                    Create Your First Event
                    <ArrowRight className="ml-2 h-5 w-5" />
                  </Button>
                </Link>
              </div>
            </div>

            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-purple-500/20 to-blue-500/20 blur-3xl rounded-3xl -z-10 rotate-3"></div>
              <div className="backdrop-blur-md bg-black/30 border border-white/10 rounded-3xl overflow-hidden shadow-[0_0_25px_rgba(149,128,255,0.3)] rotate-3">
                <Image
                  src="/eventplaceholder.png?height=600&width=800"
                  alt="Event Creation Interface"
                  width={800}
                  height={600}
                  className="w-full object-cover"
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Call to Action */}
      <section className="relative z-10 py-20 text-center bg-gradient-to-b from-transparent to-blue-900/10">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl mx-auto">
            <Badge className="mb-4 bg-white/10 hover:bg-white/20 border-0 text-black dark:text-white">
              Get Started Today
            </Badge>
            <h2 className="text-3xl md:text-5xl font-bold mb-6 leading-tight">
              Ready to Transform Your Event Experience?
            </h2>
            <p className="/70 text-lg mb-8 max-w-2xl mx-auto">
              Join thousands of organizers and attendees who are already part of
              our growing community.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href={Route.BrowseEvents}>
                <Button className="bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600 border-0 h-12 px-8 text-lg">
                  Explore Events
                </Button>
              </Link>
              <Link href={Route.CreateEvent}>
                <Button
                  variant="outline"
                  className="border-white/20 h-12 px-8 text-lg"
                >
                  Create an Event
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 border-t border-white/10 backdrop-blur-sm">
        <div className="p-5 md:p-10">
          <Logo />
          <p className="/50 text-sm py-3">
            © {new Date().getFullYear()} {siteName}. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}
