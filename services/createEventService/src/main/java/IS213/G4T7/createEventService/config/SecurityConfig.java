package IS213.G4T7.createEventService.config;

import java.util.Arrays;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.oauth2.core.DelegatingOAuth2TokenValidator;
import org.springframework.security.oauth2.core.OAuth2Error;
import org.springframework.security.oauth2.core.OAuth2TokenValidator;
import org.springframework.security.oauth2.core.OAuth2TokenValidatorResult;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.security.oauth2.jwt.JwtDecoder;
import org.springframework.security.oauth2.jwt.JwtIssuerValidator;
import org.springframework.security.oauth2.jwt.JwtTimestampValidator;
import org.springframework.security.oauth2.jwt.NimbusJwtDecoder;
import org.springframework.security.web.SecurityFilterChain;

import lombok.extern.slf4j.Slf4j;

@Slf4j
@Configuration
@EnableWebSecurity
@EnableMethodSecurity
public class SecurityConfig {

    @Value("${aws.cognito.region}")
    private String awsRegion;

    @Value("${aws.cognito.user-pool-id}")
    private String cognitoUserPoolId;

    @Value("${aws.cognito.app-client-id}")
    private String cognitoAppClientId;

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http.csrf(csrf -> csrf.disable())
            .cors(cors -> cors.configure(http))
            .sessionManagement(session ->
                    session.sessionCreationPolicy(SessionCreationPolicy.STATELESS)
            )
            .authorizeHttpRequests(authorize ->
                    authorize.requestMatchers("/actuator/**").permitAll().anyRequest().authenticated()
            )
            .oauth2ResourceServer(oauth2 -> oauth2
                .jwt(jwt -> jwt.decoder(jwtDecoder()))
            );
        return http.build();
    }

    @Bean
    public JwtDecoder jwtDecoder() {
        String jwkSetUri = String.format("https://cognito-idp.%s.amazonaws.com/%s/.well-known/jwks.json",
                awsRegion, cognitoUserPoolId);
        String issuerUri = String.format("https://cognito-idp.%s.amazonaws.com/%s",
                awsRegion, cognitoUserPoolId);

        NimbusJwtDecoder jwtDecoder = NimbusJwtDecoder.withJwkSetUri(jwkSetUri).build();

        OAuth2TokenValidator<Jwt> issuerValidator = new JwtIssuerValidator(issuerUri);
        OAuth2TokenValidator<Jwt> timestampValidator = new JwtTimestampValidator();
        OAuth2TokenValidator<Jwt> audienceValidator = token -> {
            String tokenUse = token.getClaimAsString("token_use");
            String audience = token.getClaimAsString("aud");
            String clientId = token.getClaimAsString("client_id");

            // For access tokens, verify client_id
            if ("access".equals(tokenUse)) {
                if (clientId == null || !clientId.equals(cognitoAppClientId)) {
                    log.error("Invalid client_id for access token. Expected: {}, Got: {}", cognitoAppClientId, clientId);
                    return OAuth2TokenValidatorResult.failure(
                            new OAuth2Error("invalid_token", "Invalid client_id for access token", null)
                    );
                }
                return OAuth2TokenValidatorResult.success();
            }
            
            // For ID tokens, verify audience
            if ("id".equals(tokenUse)) {
                String formattedCognitoAppClientId = String.format("[%s]", cognitoAppClientId);
                if (audience == null || !audience.equals(formattedCognitoAppClientId)) {
                    log.error("Invalid audience for ID token. Expected: {}, Got: {}", formattedCognitoAppClientId, audience);
                    return OAuth2TokenValidatorResult.failure(
                            new OAuth2Error("invalid_token", "Invalid audience for ID token", null)
                    );
                }
                return OAuth2TokenValidatorResult.success();
            }
            
            // If token_use is not specified, try both validations
            if (tokenUse == null) {
                log.info("Token use not specified, trying both validations");
                boolean hasValidClientId = clientId != null && clientId.equals(cognitoAppClientId);
                boolean hasValidAudience = audience != null && audience.equals(cognitoAppClientId);
                
                if (hasValidClientId || hasValidAudience) {
                    log.info("Token validated successfully with either client_id or audience");
                    return OAuth2TokenValidatorResult.success();
                }
                
                log.error("Token failed both client_id and audience validation");
                return OAuth2TokenValidatorResult.failure(
                        new OAuth2Error("invalid_token", "Token must have valid client_id or audience", null)
                );
            }
            
            log.error("Invalid token_use claim: {}", tokenUse);
            return OAuth2TokenValidatorResult.failure(
                    new OAuth2Error("invalid_token", "Invalid token_use claim", null)
            );
        };

        // Compose validators
        OAuth2TokenValidator<Jwt> validator = new DelegatingOAuth2TokenValidator<>(
            Arrays.asList(issuerValidator, timestampValidator, audienceValidator)
        );

        jwtDecoder.setJwtValidator(validator);
        return jwtDecoder;
    }
}
