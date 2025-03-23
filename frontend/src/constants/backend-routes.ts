export const BACKEND_ROUTES = {
    userManagementServiceUrl: process.env.NEXT_PUBLIC_USER_MANAGEMENT_SERVICE_URL || "http://localhost:5001",
    createEventServiceUrl: process.env.NEXT_PUBLIC_CREATE_EVENT_SERVICE_URL || "http://localhost:5002",
    eventsService: process.env.NEXT_PUBLIC_EVENTS_SERVICE_URL || "http://localhost:5003",
    bookingService: process.env.NEXT_PUBLIC_BOOKING_SERVICE_URL || "http://localhost:5004"
} as const;
