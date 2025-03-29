package IS213.G4T7.createEventService.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

@Data
public class EmailData {
    @JsonProperty("MainMessage")
    private String mainMessage;

    @JsonProperty("Email")
    private String email;

    @JsonProperty("Subject")
    private String subject;
}
