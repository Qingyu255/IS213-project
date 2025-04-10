package IS213.G4T7.createEventService.services.Impl;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import IS213.G4T7.createEventService.dto.AtomicServiceEventCreationDetails;
import IS213.G4T7.createEventService.dto.AtomicServiceEventCreationResponse;
import IS213.G4T7.createEventService.services.EventsService;
import IS213.G4T7.createEventService.services.Impl.exceptions.AtomicServiceEventCreationException;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@Service
public class EventsServiceImpl implements EventsService {

    @Value("${events.microservice.url}")
    private String eventsMicroserviceUrl;

    private final RestTemplate restTemplate;

    public EventsServiceImpl(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    public AtomicServiceEventCreationResponse createEvent(AtomicServiceEventCreationDetails event) throws AtomicServiceEventCreationException {
        log.info("Attempting to create event via events atomic service. AtomicServiceEventCreationDetails: {}", event);

        String url = eventsMicroserviceUrl + "/create";
        try {
            ResponseEntity<AtomicServiceEventCreationResponse> response = restTemplate.postForEntity(url, event, AtomicServiceEventCreationResponse.class);
            log.info("Received response from atomic service. Status code: {}", response.getStatusCode());
            log.info("Event created successfully via atomic service.");
            return response.getBody();
        } catch (Exception ex) {
            log.error("Exception occurred while calling atomic service: {}", ex.getMessage(), ex);
            throw new AtomicServiceEventCreationException("Failed to create event due to exception: " + ex.getMessage());
        }
    }
}