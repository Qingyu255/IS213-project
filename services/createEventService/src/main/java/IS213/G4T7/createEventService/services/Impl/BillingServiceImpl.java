package IS213.G4T7.createEventService.services.Impl;

import IS213.G4T7.createEventService.dto.AtomicServiceEventCreationResponse;
import IS213.G4T7.createEventService.dto.EventDetails;
import IS213.G4T7.createEventService.services.BillingService;
import IS213.G4T7.createEventService.services.Impl.exceptions.BillingServiceException;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

@Slf4j
@Service
public class BillingServiceImpl implements BillingService {

    @Value("${billing.microservice.url}")
    private String billingMicroserviceUrl;

    private final RestTemplate restTemplate;

    public BillingServiceImpl(RestTemplateBuilder restTemplateBuilder) {
        this.restTemplate = restTemplateBuilder.build();
    }

    public boolean verifyEventCreationPaymentCompleted(EventDetails eventDetails) throws BillingServiceException {

        log.info("Verifying payment completed for event: {}", eventDetails);
        // TODO: add rest API call to billing service
        try {
    //        String url = billingMicroserviceUrl + "/verifypayment";
    //        ResponseEntity<T> response = restTemplate.postForEntity(url, eventDetails, T.class);
    //
    //        // Throw AtomicServiceEventCreationException if not successful, else do nothing
    //        if (!response.getStatusCode().is2xxSuccessful()) {
    //            throw new BillingServiceException("Failed to verify payment. Status code: " + response.getStatusCode());
    //        }
            log.info("Successfully verified that payment completed for event: {}", eventDetails);
        } catch (Exception ex) {
            log.error("Failed to verify payment.: {}", ex.getMessage(), ex);
            throw new BillingServiceException("Failed to verify payment.: " + ex.getMessage());
        }
        return true;
    }
}
