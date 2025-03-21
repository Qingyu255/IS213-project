package IS213.G4T7.createEventService.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
                .csrf(csrf -> csrf.disable()) // Temporarily disable CSRF protection
                .authorizeHttpRequests(authz -> authz.anyRequest().permitAll())
                .httpBasic(Customizer.withDefaults());

        return http.build();
    }
}