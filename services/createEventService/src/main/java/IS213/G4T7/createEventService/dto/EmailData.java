package IS213.G4T7.createEventService.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

@Data
public class EmailData {
    @JsonProperty("To")
    private String to;

    @JsonProperty("From")
    private String from;

    @JsonProperty("Subject")
    private String subject;

    @JsonProperty("Body")
    private String body;

    @JsonProperty("IsHtml")
    private boolean isHtml;

    @JsonProperty("CC")
    private String cc;

    @JsonProperty("BCC")
    private String bcc;
}
