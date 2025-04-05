import { InterestCategory } from "@/enums/InterestCategory";

export type EventDetails = {
  id: string;
  title: string;
  description: string;
  // Using snake case to match with backend payload oop
  startDateTime: string;
  endDateTime?: string; // optional if the event has a defined end time

  // Structured venue information
  venue: {
    address: string;
    name: string;
    city: string;
    state: string;
    additionalDetails?: string;
    coordinates: {
      lat: number;
      lng: number;
    };
  };
  imageUrl: string;
  categories: InterestCategory[];

  // Assume price is in SGD (temporary till multi currency is supported)
  price: number;

  // // Schedule items can include more details if needed
  // schedule?: {
  //   startTime: string;
  //   endTime?: string;
  //   title: string;
  //   description?: string;
  // }[];

  // Enhanced organizer details
  organizer: {
    id: string;
    username: string;
  };
  capacity: number; // maximum allowed attendees
};

export interface EventWithTickets extends EventDetails {
  ticketInfo?: {
    availableTickets: number | "Unlimited";
    totalCapacity: number | "Unlimited";
    bookedTickets: number;
  };
}

