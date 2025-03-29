package IS213.G4T7.createEventService.security;

import java.io.IOException;

import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@Component
public class AuthTokenFilter extends OncePerRequestFilter {
    @Override
    protected void doFilterInternal(
        HttpServletRequest request,
        HttpServletResponse response,
        FilterChain filterChain
    ) throws ServletException, IOException {
        try {
            String token = request.getHeader("Authorization");
            if (token != null) {
                log.info("Received Authorization header");
                log.debug("Raw token: {}", token);
                
                // Ensure token starts with "Bearer "
                if (!token.startsWith("Bearer ")) {
                    token = "Bearer " + token;
                    log.debug("Added 'Bearer ' prefix to token");
                }
                
                AuthTokenHolder.setToken(token);
                log.info("Stored bearer token in AuthTokenHolder");
                log.debug("Token format: {}", token.startsWith("Bearer ") ? "Correct" : "Incorrect");
            } else {
                log.warn("No Authorization header found in request");
            }
            filterChain.doFilter(request, response);
        } catch (Exception e) {
            log.error("Error in AuthTokenFilter: {}", e.getMessage(), e);
            throw e;
        }
    }
}
