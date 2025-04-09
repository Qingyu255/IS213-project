export const BACKEND_ROUTES = {
    userManagementServiceUrl: process.env.NEXT_PUBLIC_USER_MANAGEMENT_SERVICE_API_BASE_URL ,
    createEventServiceUrl: process.env.NEXT_PUBLIC_CREATE_EVENTS_SERVICE_API_BASE_URL ,
    eventsService: process.env.EVENT_SERVICE_URL ,
    billingService: process.env.BILLING_SERVICE_URL ,
    ticketManagementService: process.env.TICKET_SERVICE_URL ,
    bookingService: process.env.BOOKING_SERVICE_URL ,
    refundService: process.env.REFUND_SERVICE_URL ,
    kong: process.env.NEXT_PUBLIC_KONG_API_BASE_URL ?? "http://localhost:8100"
};