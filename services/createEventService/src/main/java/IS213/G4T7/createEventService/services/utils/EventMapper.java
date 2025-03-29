package IS213.G4T7.createEventService.services.utils;

import java.time.LocalDateTime;
import java.time.ZoneOffset;
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

        // Parse ISO 8601 date strings and convert to UTC
        LocalDateTime startDateTime = LocalDateTime.parse(eventDetails.getStartDateTime(), ISO_FORMATTER);
        atomic.setStartDateTime(startDateTime.atOffset(ZoneOffset.UTC));
        
        if (eventDetails.getEndDateTime() != null && !eventDetails.getEndDateTime().isEmpty()) {
            LocalDateTime endDateTime = LocalDateTime.parse(eventDetails.getEndDateTime(), ISO_FORMATTER);
            atomic.setEndDateTime(endDateTime.atOffset(ZoneOffset.UTC));
        }

        atomic.setImageUrl(eventDetails.getImageUrl());
        atomic.setVenue(eventDetails.getVenue());
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