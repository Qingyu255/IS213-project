package IS213.G4T7.createEventService.dto;

import java.time.OffsetDateTime;
import java.util.List;

import lombok.Data;

@Data
public class AtomicServiceEventCreationDetails {
    private String id;
    private String title;
    private String description;
    private OffsetDateTime startDateTime;
    private OffsetDateTime endDateTime; // optional
    private String imageUrl;
    private EventDetails.Venue venue;
    private double price;
    private int capacity;
    private List<String> categories;
    private EventDetails.Organizer organizer;
}
