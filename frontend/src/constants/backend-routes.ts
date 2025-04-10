const KONG_GATEWAY_URL = process.env.NEXT_PUBLIC_KONG_API_BASE_URL ?? "http://localhost:8100";
const IS_SERVER = typeof window === 'undefined';

// Internal Docker network URLs for server-side calls
const SERVER_URLS = {
    bookingService: process.env.BOOKING_SERVICE_URL ?? "http://booking-service:8002",
    ticketManagementService: process.env.TICKET_SERVICE_URL ?? "http://ticket-management-service:8000",
    eventsService: process.env.EVENT_SERVICE_URL ?? "http://events-service:8001",
    billingService: process.env.BILLING_SERVICE_URL ?? "http://billing-service:5001",
    userManagementServiceUrl: process.env.USER_MANAGEMENT_SERVICE_API_BASE_URL ?? "http://user-management-service:8080",
    createEventServiceUrl: process.env.CREATE_EVENT_SERVICE_URL ?? "http://create-event-service:8070",
    refundService: "http://refund-composite-service:8880"
};

// Kong Gateway URLs for client-side calls
const CLIENT_URLS = {
    bookingService: KONG_GATEWAY_URL,
    ticketManagementService: KONG_GATEWAY_URL,
    eventsService: KONG_GATEWAY_URL,
    billingService: KONG_GATEWAY_URL,
    userManagementServiceUrl: KONG_GATEWAY_URL,
    createEventServiceUrl: KONG_GATEWAY_URL,
    refundService: KONG_GATEWAY_URL
};

export const BACKEND_ROUTES = IS_SERVER ? SERVER_URLS : CLIENT_URLS;
