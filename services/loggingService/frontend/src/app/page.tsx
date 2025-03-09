import Link from "next/link";
import Image from "next/image";
import {
  Calendar,
  ChevronRight,
  Clock,
  MapPin,
  Star,
  Ticket,
  Users,
  PlusCircle,
  ArrowRight,
  BarChart,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { siteName } from "@/constants/common";
import { Route } from "@/enums/Route";
import Logo from "@/components/logo";

export default function EventPlatformPage() {
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
      <section className="relative z-10 py-20 md:py-32">
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

          {/* Platform Preview */}
          <div className="relative mt-16 mx-auto max-w-5xl">
            <div className="absolute inset-0 bg-gradient-to-r from-purple-500/20 to-blue-500/20 blur-3xl rounded-3xl -z-10"></div>
            <div className="backdrop-blur-md bg-black/40 border border-white/10 rounded-3xl overflow-hidden shadow-[0_0_25px_rgba(149,128,255,0.3)]">
              <Image
                src="/placeholder.svg?height=600&width=1200"
                alt="Platform Preview"
                width={1200}
                height={600}
                className="w-full object-cover"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Featured Events */}
      {/* TODO: Fetch Events from events service */}
      <section className="relative z-10 py-20">
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
              {/* <Button
                variant="outline"
                className="border-white/20 hover:bg-white/10"
              >
                All Categories
              </Button> */}
              <Link href={Route.BrowseEvents}>
                <Button variant="outline">
                  View All <ChevronRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              {
                name: "Future of AI Conference",
                image: "/placeholder.svg?height=400&width=600",
                date: "June 15, 2025",
                time: "9:00 AM - 5:00 PM",
                location: "Tech Hub, San Francisco",
                price: "$99",
                attendees: 1240,
                category: "Technology",
              },
              {
                name: "Electronic Music Festival",
                image: "/placeholder.svg?height=400&width=600",
                date: "July 22-25, 2025",
                time: "8:00 PM - 2:00 AM",
                location: "Quantum Arena, Los Angeles",
                price: "$149",
                attendees: 5000,
                category: "Music",
              },
              {
                name: "Creative Design Workshop",
                image: "/placeholder.svg?height=400&width=600",
                date: "August 10, 2025",
                time: "10:00 AM - 4:00 PM",
                location: "Design Center, New York",
                price: "$75",
                attendees: 120,
                category: "Workshop",
              },
            ].map((event, index) => (
              <Card
                key={index}
                className="bg-white/5 border-white/10 overflow-hidden hover:shadow-[0_0_15px_rgba(149,128,255,0.3)] transition-all duration-300 group"
              >
                <div className="relative">
                  <Image
                    src={event.image || "/placeholder.svg"}
                    alt={event.name}
                    width={600}
                    height={400}
                    className="w-full h-60 object-cover transition-transform duration-500 group-hover:scale-110"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent" />
                  <Badge className="absolute top-4 left-4 bg-purple-500/80 hover:bg-purple-500  border-0">
                    {event.category}
                  </Badge>
                  <div className="absolute bottom-4 left-4 right-4">
                    <h3 className="text-xl font-bold mb-2">{event.name}</h3>
                    <div className="flex items-center /70 text-sm">
                      <Calendar className="h-4 w-4 mr-2" />
                      <span>{event.date}</span>
                    </div>
                  </div>
                </div>
                <CardContent className="p-4">
                  <div className="space-y-3">
                    <div className="flex items-center /70 text-sm">
                      <Clock className="h-4 w-4 mr-2" />
                      <span>{event.time}</span>
                    </div>
                    <div className="flex items-center /70 text-sm">
                      <MapPin className="h-4 w-4 mr-2" />
                      <span>{event.location}</span>
                    </div>
                    <div className="flex items-center /70 text-sm">
                      <Users className="h-4 w-4 mr-2" />
                      <span>{event.attendees} attending</span>
                    </div>
                    <div className="flex justify-between items-center pt-3 border-t border-white/10">
                      <span className="font-bold">{event.price}</span>
                      <Button
                        variant="ghost"
                        className="bg-white/5 hover:bg-white/10 "
                      >
                        Get Tickets
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
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
                    icon: <Ticket className="h-6 w-6 text-blue-400" />,
                    title: "Seamless Ticketing",
                    description:
                      "Sell tickets, manage registrations, and control capacity effortlessly.",
                  },
                  {
                    icon: <BarChart className="h-6 w-6 text-cyan-400" />,
                    title: "Powerful Analytics",
                    description:
                      "Get real-time insights into attendance, engagement, and revenue.",
                  },
                ].map((feature, index) => (
                  <div key={index} className="flex gap-4">
                    <div className="bg-white/10 w-12 h-12 rounded-full flex items-center justify-center shrink-0">
                      {feature.icon}
                    </div>
                    <div>
                      <h3 className="text-xl font-bold mb-1">
                        {feature.title}
                      </h3>
                      <p className="/70">{feature.description}</p>
                    </div>
                  </div>
                ))}
              </div>
              <Link href={Route.CreateEvent}>
                <Button className="mt-8 bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600  border-0">
                  Start Creating <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
            </div>

            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-purple-500/20 to-blue-500/20 blur-3xl rounded-3xl -z-10"></div>
              <div className="backdrop-blur-md bg-black/40 border border-white/10 rounded-3xl overflow-hidden shadow-[0_0_25px_rgba(149,128,255,0.3)]">
                <Image
                  src="/placeholder.svg?height=600&width=800"
                  alt="Event Creation Dashboard"
                  width={800}
                  height={600}
                  className="w-full object-cover"
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="relative z-10 py-20">
        <div className="container mx-auto px-4">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <Badge className="mb-4 bg-white/10 hover:bg-white/20 border-0 text-black dark:text-white">
              Simple Process
            </Badge>
            <h2 className="text-3xl md:text-4xl font-bold mb-6">
              How {siteName} Works
            </h2>
            <p className="/70 text-lg">
              Whether you&apos;re attending or creating, our platform makes the
              entire process seamless and enjoyable.
            </p>
          </div>

          <Tabs defaultValue="attend" className="w-full max-w-4xl mx-auto">
            <TabsList className="grid grid-cols-2 mb-12 p-1 w-80 mx-auto">
              <TabsTrigger value="attend" className="rounded-md">
                Attending
              </TabsTrigger>
              <TabsTrigger value="create" className="rounded-md">
                Creating
              </TabsTrigger>
            </TabsList>

            <TabsContent value="attend" className="mt-0">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {[
                  {
                    step: "01",
                    title: "Discover Events",
                    description:
                      "Browse through thousands of events or search for specific categories, dates, or locations.",
                  },
                  {
                    step: "02",
                    title: "Secure Your Spot",
                    description:
                      "Register or purchase tickets in just a few clicks with our secure payment system.",
                  },
                  {
                    step: "03",
                    title: "Enjoy the Experience",
                    description:
                      "Get automatic reminders, digital tickets, and seamless check-in at the event.",
                  },
                ].map((step, index) => (
                  <Card
                    key={index}
                    className="backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-6 hover:shadow-[0_0_15px_rgba(149,128,255,0.2)] transition-all duration-300"
                  >
                    <div className="bg-gradient-to-r from-purple-500 to-blue-500  w-12 h-12 rounded-full flex items-center justify-center mb-6 text-xl font-bold">
                      {step.step}
                    </div>
                    <h3 className="text-xl font-bold mb-4">{step.title}</h3>
                    <p className="/70">{step.description}</p>
                  </Card>
                ))}
              </div>
            </TabsContent>

            <TabsContent value="create" className="mt-0">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {[
                  {
                    step: "01",
                    title: "Set Up Your Event",
                    description:
                      "Create a stunning event page with our drag-and-drop builder, no design skills required.",
                  },
                  {
                    step: "02",
                    title: "Manage Registrations",
                    description:
                      "Configure ticket types, prices, and capacity. Track sales and attendees in real-time.",
                  },
                  {
                    step: "03",
                    title: "Promote & Analyze",
                    description:
                      "Share your event across platforms and gain insights with comprehensive analytics.",
                  },
                ].map((step, index) => (
                  <Card
                    key={index}
                    className="backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-6 hover:shadow-[0_0_15px_rgba(149,128,255,0.2)] transition-all duration-300"
                  >
                    <div className="bg-gradient-to-r from-purple-500 to-blue-500  w-12 h-12 rounded-full flex items-center justify-center mb-6 text-xl font-bold">
                      {step.step}
                    </div>
                    <h3 className="text-xl font-bold mb-4">{step.title}</h3>
                    <p className="/70">{step.description}</p>
                  </Card>
                ))}
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </section>

      {/* Testimonials */}
      <section className="relative z-10 py-20 bg-gradient-to-b from-transparent to-blue-900/10">
        <div className="container mx-auto px-4">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <Badge className="mb-4 bg-white/10 hover:bg-white/20 border-0 text-black dark:text-white">
              Success Stories
            </Badge>
            <h2 className="text-3xl md:text-4xl font-bold mb-6">
              What Our Users Say
            </h2>
            <p className="/70 text-lg">
              Join thousands of event creators and attendees who have
              transformed their event experience with {siteName}.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-5xl mx-auto">
            {[
              {
                name: "Sarah Johnson",
                role: "Event Organizer",
                avatar: "/placeholder.svg?height=100&width=100",
                comment:
                  "{siteName} transformed how I run my workshops. The platform is intuitive, and the analytics help me understand my audience better. My ticket sales have increased by 40% since switching!",
              },
              {
                name: "Michael Chen",
                role: "Conference Attendee",
                avatar: "/placeholder.svg?height=100&width=100",
                comment:
                  "I've discovered amazing events I would have never found otherwise. The booking process is seamless, and I love getting personalized recommendations based on my interests.",
              },
              {
                name: "Jessica Williams",
                role: "Festival Producer",
                avatar: "/placeholder.svg?height=100&width=100",
                comment:
                  "As someone who runs multiple events per year, {siteName} has been a game-changer. The ability to clone events, customize ticketing, and track performance all in one place is invaluable.",
              },
              {
                name: "David Rodriguez",
                role: "Tech Meetup Organizer",
                avatar: "/placeholder.svg?height=100&width=100",
                comment:
                  "The promotional tools are fantastic! I can easily share my events across platforms, and the built-in SEO features help new attendees discover my meetups. Highly recommended!",
              },
            ].map((testimonial, index) => (
              <Card
                key={index}
                className="backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-6 hover:shadow-[0_0_15px_rgba(149,128,255,0.2)] transition-all duration-300"
              >
                <div className="flex items-center mb-6">
                  <Image
                    src={testimonial.avatar || "/placeholder.svg"}
                    alt={testimonial.name}
                    width={60}
                    height={60}
                    className="rounded-full border-2 border-purple-500"
                  />
                  <div className="ml-4">
                    <h4 className="font-bold text-lg">{testimonial.name}</h4>
                    <p className="/70">{testimonial.role}</p>
                  </div>
                </div>
                <p className="/90 italic">{`"${testimonial.comment}"`}</p>
                <div className="mt-4 flex">
                  {[...Array(5)].map((_, i) => (
                    <Star
                      key={i}
                      className="h-4 w-4 text-yellow-400 fill-yellow-400"
                    />
                  ))}
                </div>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="relative z-10 py-20">
        <div className="container mx-auto px-4">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <Badge className="mb-4 bg-white/10 hover:bg-white/20 border-0 text-black dark:text-white">
              Flexible Plans
            </Badge>
            <h2 className="text-3xl md:text-4xl font-bold mb-6">
              Choose the Perfect Plan
            </h2>
            <p className="/70 text-lg">
              Whether you&apos;re hosting a small workshop or a large festival,
              we have the right plan for you.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {[
              {
                name: "Starter",
                price: "$0",
                period: "Forever Free",
                description:
                  "Perfect for occasional event creators or small gatherings.",
                features: [
                  "Up to 50 attendees per event",
                  "Basic event page customization",
                  "Email notifications",
                  "Standard support",
                ],
                cta: "Get Started",
                highlight: false,
              },
              {
                name: "Professional",
                price: "$29",
                period: "per month",
                description:
                  "Ideal for regular event creators looking to grow their audience.",
                features: [
                  "Up to 500 attendees per event",
                  "Advanced customization options",
                  "Ticket types & promo codes",
                  "Analytics dashboard",
                  "Priority support",
                ],
                cta: "Start Free Trial",
                highlight: true,
              },
              {
                name: "Enterprise",
                price: "$99",
                period: "per month",
                description:
                  "For large-scale events and professional organizers.",
                features: [
                  "Unlimited attendees",
                  "White-label experience",
                  "Advanced analytics & reporting",
                  "API access",
                  "Dedicated account manager",
                ],
                cta: "Contact Sales",
                highlight: false,
              },
            ].map((plan, index) => (
              <Card
                key={index}
                className={`${
                  plan.highlight
                    ? "bg-white/10 border-purple-500"
                    : "bg-white/5"
                } rounded-2xl p-8 hover:shadow-[0_0_15px_rgba(149,128,255,0.2)] transition-all duration-300 relative`}
              >
                {plan.highlight && (
                  <div className="absolute top-0 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-gradient-to-r from-purple-500 to-blue-500  px-4 py-1 rounded-full text-sm font-medium">
                    Most Popular
                  </div>
                )}
                <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
                <div className="mb-4">
                  <span className="text-4xl font-bold">{plan.price}</span>
                  <span className="/70 ml-1">{plan.period}</span>
                </div>
                <p className="/70 mb-6">{plan.description}</p>
                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature, i) => (
                    <li key={i} className="flex items-start">
                      <div className="bg-gradient-to-r from-purple-500 to-blue-500 rounded-full p-1 mr-3 mt-0.5">
                        <svg
                          width="12"
                          height="12"
                          viewBox="0 0 24 24"
                          fill="none"
                          xmlns="http://www.w3.org/2000/svg"
                        >
                          <path
                            d="M5 12L10 17L20 7"
                            stroke="white"
                            strokeWidth="2"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                          />
                        </svg>
                      </div>
                      {feature}
                    </li>
                  ))}
                </ul>
                <Button
                  className={`w-full ${
                    plan.highlight
                      ? "bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600 "
                      : "hover:bg-white/20 "
                  } border-0`}
                >
                  {plan.cta}
                </Button>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative z-10 py-20">
        <div className="container mx-auto px-4">
          <div className="max-w-5xl mx-auto backdrop-blur-md bg-gradient-to-r from-purple-900/30 to-blue-900/30 border border-white/10 rounded-2xl p-12 text-center">
            <h2 className="text-3xl md:text-4xl font-bold mb-6">
              Ready to Transform Your Events?
            </h2>
            <p className="/70 text-lg mb-8 max-w-2xl mx-auto">
              Join thousands of event creators and attendees on the platform
              that&apos;s redefining the event experience.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href={Route.CreateEvent} className="rounded-lg bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600  border-0 px-8 py-6 text-lg">
                Get Started for Free
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
