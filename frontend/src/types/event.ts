export type EventDetails = {
    id: string;
    title: string;
    date: string;
    time: string;
    location: string;
    address: string;
    coordinates: {
      lat: number;
      lng: number;
    };
    image: string;
    category: string;
    price: string;
    description: string;
    schedule: {
      time: string;
      title: string;
    }[];
    organizer: {
      name: string;
      image: string;
      description: string;
    };
    attendees: {
      id: string;
      name: string;
      image: string;
    }[];
    totalAttendees: number;
  }
  