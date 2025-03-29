package IS213.G4T7.createEventService.security;

public class AuthTokenHolder {
    private static String authToken;

    public static synchronized void setToken(String token) {
        authToken = token;
    }

    public static synchronized String getToken() {
        return authToken;
    }

    public static synchronized void clear() {
        authToken = null;
    }
}