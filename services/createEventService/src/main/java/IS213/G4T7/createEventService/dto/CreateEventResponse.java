package IS213.G4T7.createEventService.dto;

import lombok.Data;

@Data
public class CreateEventResponse {
    private String message;
    private String error;

    public CreateEventResponse(String message) {
        this.message = message;
    }

    public CreateEventResponse(String message, String error) {
        this.message = message;
        this.error = error;
    }
}
