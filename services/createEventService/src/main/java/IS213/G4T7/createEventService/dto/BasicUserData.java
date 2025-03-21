package IS213.G4T7.createEventService.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

@Data
public class BasicUserData {
    @JsonProperty("Id")
    public String id;

    @JsonProperty("Username")
    public String username;

    @JsonProperty("Email")
    public String email;
}
