package IS213.G4T7.createEventService.security;

public class AuthTokenHolder {
    private static final ThreadLocal<String> authToken = new ThreadLocal<>();

    public static void setToken(String token) {
        authToken.set(token);
    }

    public static String getToken() {
        return authToken.get();
    }

    public static void clear() {
        authToken.remove();
    }
}