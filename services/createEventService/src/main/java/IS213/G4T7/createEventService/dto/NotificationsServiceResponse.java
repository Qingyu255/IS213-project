package IS213.G4T7.createEventService.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

@Data
public class NotificationsServiceResponse {
    @JsonProperty("ErrorMsg") // Not sure why the response uses ErrorMsg for success message too but yes
    private String message;
    @JsonProperty("Success")
    private boolean success;
    @JsonProperty("Errors")
    private String[] errors = null;
    @JsonProperty("StatusCode")
    private int statusCode = 200; // For Notifications service, if not status code returned means okay 200
}
