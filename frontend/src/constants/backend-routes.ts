export const BACKEND_ROUTES = {
    userManagementServiceUrl: process.env.NEXT_PUBLIC_USER_MANAGEMENT_SERVICE_API_BASE_URL ?? "",
    createEventServiceUrl: process.env.NEXT_PUBLIC_CREATE_EVENTS_SERVICE_API_BASE_URL ?? "http://localhost:8070",
    eventsService: process.env.NEXT_PUBLIC_EVENTS_SERVICE_API_BASE_URL ?? "http://localhost:8001",
    billingService: process.env.NEXT_PUBLIC_EVENTS_SERVICE_API_BASE_URL ?? "http://localhost:5001",
}
