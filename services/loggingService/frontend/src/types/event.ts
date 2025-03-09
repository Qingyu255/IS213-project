import { InterestCategory } from "@/enums/InterestCategory";

export type EventDetails = {
  id: string;
  title: string;
  description: string;
  // Use ISO 8601 for date-time handling
  startDateTime: string; 
  endDateTime?: string; // optional if the event has a defined end time

  // Structured venue information
  venue: {
    address: string;
    name: string
    city: string;
    state: string;
    additionalDetails?: string;
    coordinates: {
      lat: number;
      lng: number;
    };
  };

  imageUrl: string;

  // Define category as string, or potentially an enum/union type
  category: InterestCategory;

  // Price as an object to include amount and currency
  price: {
    amount: number;
    currency: string;
  };

  // Schedule items can include more details if needed
  schedule?: {
    startTime: string;
    endTime?: string;
    title: string;
    description?: string;
  }[];

  // Enhanced organizer details
  organizer: {
    id: string;
    username: string;
    // imageUrl?: string;
    // description?: string;
    // contactEmail?: string;
  };

  // Attendees information
  attendees: {
    id: string;
    name: string;
    imageUrl?: string;
  }[];
  totalAttendees: number;
  capacity?: number; // maximum allowed attendees

  // Invite-only functionality
  eventType: string; // for now: public and private only
  invitedEmails?: string[]; // optional list of emails for invite-only events

  // Timestamps for record keeping
  createdAt?: string;
  updatedAt?: string;
};
