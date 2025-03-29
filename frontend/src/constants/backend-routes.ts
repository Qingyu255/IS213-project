export const KONG_GATEWAY_URL = "http://localhost:10000";

export const BACKEND_ROUTES = {
    userManagementServiceUrl: KONG_GATEWAY_URL ?? "",
    createEventServiceUrl: KONG_GATEWAY_URL ?? "http://localhost:8070",
    eventsService: KONG_GATEWAY_URL ?? "http://localhost:8001",
    billingService: KONG_GATEWAY_URL ?? "http://localhost:5001",
}
