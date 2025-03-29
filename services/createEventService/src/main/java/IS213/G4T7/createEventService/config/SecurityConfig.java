package IS213.G4T7.createEventService.config;

import java.util.Arrays;
import java.util.Collection;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.convert.converter.Converter;
import org.springframework.security.authentication.AbstractAuthenticationToken;
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
        System.out.println("Configuring SecurityFilterChain...");
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
        System.out.println("SecurityFilterChain configured successfully.");
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
        OAuth2TokenValidator<Jwt> clientIdValidator = token -> {
             String clientId = token.getClaimAsString("client_id");
             if (clientId == null || !clientId.equals(cognitoAppClientId)) {
                 return OAuth2TokenValidatorResult.failure(
                         new OAuth2Error("invalid_token", "Invalid client_id claim", null)
                 );
             }
             return OAuth2TokenValidatorResult.success();
         };
        OAuth2TokenValidator<Jwt> timestampValidator = new JwtTimestampValidator();

        // Compose validators
        OAuth2TokenValidator<Jwt> validator = new DelegatingOAuth2TokenValidator<>(
            Arrays.asList(issuerValidator, clientIdValidator, timestampValidator)
        );

        jwtDecoder.setJwtValidator(validator);
        System.out.println("JWT Decoder configured with validators.");
        return jwtDecoder;
    }
}
