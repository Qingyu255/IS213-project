const KONG_GATEWAY_URL = process.env.NEXT_PUBLIC_KONG_API_BASE_URL ?? "http://localhost:8100";

export const BACKEND_ROUTES = {
    userManagementServiceUrl: KONG_GATEWAY_URL,
    createEventServiceUrl: KONG_GATEWAY_URL,
    eventsService: KONG_GATEWAY_URL,
    billingService: KONG_GATEWAY_URL,
    ticketManagementService: KONG_GATEWAY_URL,
    bookingService: KONG_GATEWAY_URL,
    refundService: KONG_GATEWAY_URL
};
