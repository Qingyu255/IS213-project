package IS213.G4T7.createEventService.services.Impl;

import java.util.Map;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.util.UriComponentsBuilder;

import IS213.G4T7.createEventService.dto.EventDetails;
import IS213.G4T7.createEventService.services.BillingService;
import IS213.G4T7.createEventService.services.Impl.exceptions.BillingServiceException;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@Service
public class BillingServiceImpl implements BillingService {

    @Value("${billing.microservice.url}")
    private String billingMicroserviceUrl;

    private final RestTemplate restTemplate;
    
    // Retry configuration
    private static final int MAX_RETRIES = 3;
    private static final long INITIAL_BACKOFF_MS = 1000; // 1 second

    public BillingServiceImpl(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    @Override
    public boolean verifyEventCreationPaymentCompleted(EventDetails eventDetails) throws BillingServiceException {
        log.info("Verifying payment completed for event ID: {}, organizer ID: {}", 
                eventDetails.getId(), eventDetails.getOrganizer().getId());
        
        String eventId = eventDetails.getId();
        String organizerId = eventDetails.getOrganizer().getId();
        
        if (eventId == null || eventId.isEmpty()) {
            throw new BillingServiceException("Event ID is required for payment verification");
        }
        
        if (organizerId == null || organizerId.isEmpty()) {
            throw new BillingServiceException("Organizer ID is required for payment verification");
        }
        
        String verifyUrl = UriComponentsBuilder.fromHttpUrl(billingMicroserviceUrl)
                .path("/api/events/verify-payment")
                .queryParam("event_id", eventId)
                .queryParam("organizer_id", organizerId)
                .toUriString();
        
        int retryCount = 0;
        long backoffMs = INITIAL_BACKOFF_MS;
        
        while (retryCount < MAX_RETRIES) {
            try {
                log.info("Attempting to verify payment (attempt {}/{})", retryCount + 1, MAX_RETRIES);
                
                ResponseEntity<Map> response = restTemplate.getForEntity(verifyUrl, Map.class);
                
                if (!response.getStatusCode().is2xxSuccessful()) {
                    log.warn("Failed to verify payment. Status code: {}", response.getStatusCode());
                    throw new BillingServiceException("Failed to verify payment. Status code: " + response.getStatusCode());
                }
                
                Map<String, Object> responseBody = response.getBody();
                
                if (responseBody == null) {
                    throw new BillingServiceException("Empty response from billing service");
                }
                
                Boolean success = (Boolean) responseBody.get("success");
                Boolean isPaid = (Boolean) responseBody.get("is_paid");
                
                if (Boolean.TRUE.equals(success) && Boolean.TRUE.equals(isPaid)) {
                    log.info("Successfully verified payment for event ID: {}, organizer ID: {}", 
                            eventId, organizerId);
                    return true;
                } else {
                    String errorMessage = responseBody.containsKey("error") ? 
                            responseBody.get("error").toString() : 
                            "Payment not verified for event";
                    log.warn("Payment verification failed: {}", errorMessage);
                    throw new BillingServiceException(errorMessage);
                }
                
            } catch (RestClientException e) {
                retryCount++;
                if (retryCount >= MAX_RETRIES) {
                    log.error("Failed to verify payment after {} attempts", MAX_RETRIES, e);
                    throw new BillingServiceException("Failed to verify payment after " + MAX_RETRIES + " attempts: " + e.getMessage());
                }
                
                log.warn("Attempt {} failed, retrying in {} ms", retryCount, backoffMs);
                try {
                    Thread.sleep(backoffMs);
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                }
                backoffMs *= 2; // Exponential backoff
            }
        }
        
        throw new BillingServiceException("Failed to verify payment after " + MAX_RETRIES + " attempts");
    }
}
