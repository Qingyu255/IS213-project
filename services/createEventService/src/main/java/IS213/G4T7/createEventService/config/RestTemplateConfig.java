package IS213.G4T7.createEventService.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestTemplate;

import IS213.G4T7.createEventService.security.AuthTokenHolder;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@Configuration
public class RestTemplateConfig {

    @Bean
    public RestTemplate restTemplate() {
        RestTemplate restTemplate = new RestTemplate();
        restTemplate.getInterceptors().add((request, body, execution) -> {
            String token = AuthTokenHolder.getToken();
            if (token != null) {
                // Ensure token starts with "Bearer "
                if (!token.startsWith("Bearer ")) {
                    token = "Bearer " + token;
                }
                request.getHeaders().set("Authorization", token);
                log.info("Forwarding Bearer Token to downstream service: {}", request.getURI());
            } else {
                log.error("No token found in AuthTokenHolder for request to: {}", request.getURI());
            }
            return execution.execute(request, body);
        });
        return restTemplate;
    }
}