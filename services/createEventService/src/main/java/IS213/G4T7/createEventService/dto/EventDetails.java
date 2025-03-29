package IS213.G4T7.createEventService.dto;

import lombok.Data;

import java.util.List;

@Data
public class EventDetails {
    private String id;
    private String title;
    private String description;
    private String startDateTime;
    private String endDateTime; // optional

    private Venue venue;
    private String imageUrl;
    private List<String> categories;
    private double price;
    private Organizer organizer;
    private Integer capacity; // optional

    @Data
    public static class Venue {
        private String address;
        private String name;
        private String city;
        private String state;
        private String additionalDetails; // optional
        private Coordinates coordinates;

        @Data
        public static class Coordinates {
            private double lat;
            private double lng;
        }
    }

    @Data
    public static class Organizer {
        private String id;
        private String username;
    }
}
