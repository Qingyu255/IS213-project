export const BACKEND_ROUTES = {
    userManagementServiceUrl: process.env.NEXT_PUBLIC_USER_MANAGEMENT_SERVICE_API_BASE_URL ?? "",
    createEventServiceUrl: process.env.NEXT_PUBLIC_CREATE_EVENTS_SERVICE_API_BASE_URL ?? "http://localhost:8070",
    eventsService: process.env.NEXT_PUBLIC_EVENTS_SERVICE_API_BASE_URL ?? "http://localhost:8001",
    billingService: process.env.NEXT_PUBLIC_BILLING_SERVICE_API_BASE_URL ?? "http://localhost:5001",
    ticketManagementService: process.env.NEXT_PUBLIC_TICKET_MANAGEMENT_SERVICE_API_BASE_URL ?? "http://localhost:8000",
    bookingService: process.env.NEXT_PUBLIC_BOOKING_SERVICE_API_BASE_URL ?? "http://localhost:8002",
    refundService: process.env.NEXT_PUBLIC_REFUND_SERVICE_API_BASE_URL ?? "http://localhost:8880",
    kong: process.env.NEXT_PUBLIC_KONG_API_BASE_URL ?? "http://localhost:8100"
};
