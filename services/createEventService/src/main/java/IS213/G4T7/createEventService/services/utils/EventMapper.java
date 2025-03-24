package IS213.G4T7.createEventService.services.utils;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.stream.Collectors;

import com.fasterxml.jackson.databind.ObjectMapper;

import IS213.G4T7.createEventService.dto.AtomicServiceEventCreationDetails;
import IS213.G4T7.createEventService.dto.EventDetails;

public class EventMapper {

    private static final DateTimeFormatter ISO_FORMATTER = DateTimeFormatter.ISO_DATE_TIME;
    private static final ObjectMapper objectMapper = new ObjectMapper();

    public static AtomicServiceEventCreationDetails toAtomic(EventDetails eventDetails) {
        AtomicServiceEventCreationDetails atomic = new AtomicServiceEventCreationDetails();

        atomic.setId(eventDetails.getId());
        atomic.setTitle(eventDetails.getTitle());
        atomic.setDescription(eventDetails.getDescription());

        // Parse ISO 8601 date strings
        atomic.setStartDateTime(LocalDateTime.parse(eventDetails.getStartDateTime(), ISO_FORMATTER));
        if (eventDetails.getEndDateTime() != null && !eventDetails.getEndDateTime().isEmpty()) {
            atomic.setEndDateTime(LocalDateTime.parse(eventDetails.getEndDateTime(), ISO_FORMATTER));
        }

        atomic.setImageUrl(eventDetails.getImageUrl());
        atomic.setVenue(eventDetails.getVenue());
        // Serialize the venue object to a JSON string if present; otherwise, use "{}"
//        try {
//            atomic.setVenue(eventDetails.getVenue() != null
//                    ? objectMapper.writeValueAsString(eventDetails.getVenue())
//                    : "{}");
//        } catch (JsonProcessingException e) {
//            atomic.setVenue("{}");
//        }

        atomic.setPrice(eventDetails.getPrice()); // Assume is in SGD
        atomic.setCapacity(eventDetails.getCapacity() != null ? eventDetails.getCapacity() : 0);
        // KIV: allow multiple categories to be specified for each event from the frontend
        atomic.setCategories(
            eventDetails.getCategories()
                .stream()
                .map(String::toLowerCase)
                .collect(Collectors.toList())
        );
        atomic.setOrganizer(eventDetails.getOrganizer());

        return atomic;
    }
}