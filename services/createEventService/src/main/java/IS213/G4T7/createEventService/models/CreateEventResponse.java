package IS213.G4T7.createEventService.models;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
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
