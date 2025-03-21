package IS213.G4T7.createEventService.dto;

import lombok.Data;
import java.math.BigDecimal;
import java.time.OffsetDateTime;
import java.util.List;

@Data
public class AtomicServiceEventCreationResponse {
    private String message;
    private String id;
    private String title;
    private String description;
    private OffsetDateTime startDateTime;
    private OffsetDateTime endDateTime;
    private String imageUrl;
    private String venue;
    private BigDecimal price;
    private int capacity;
    private List<String> categories;
    private EventDetails.Organizer organizer;
}
