package IS213.G4T7.createEventService.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

@Data
public class LogMessage {
    @JsonProperty("service_name")
    private String serviceName;
    private String level;
    private String message;
    @JsonProperty("transaction_id")
    private String transactionId;

    public LogMessage(String level, String message) {
        this.serviceName = "createEventService";
        this.level = level;
        this.message = message;
        this.transactionId = "no-applicable-transaction-id";
    }

    public LogMessage(String level, String message, String transactionId) {
        this.serviceName = "createEventService";
        this.level = level;
        this.message = message;
        this.transactionId = transactionId;
    }

    @Override
    public String toString() {
        return "LogMessage{" +
                "service_name='" + serviceName + '\'' +
                ", level='" + level + '\'' +
                ", message='" + message + '\'' +
                ", transaction_id='" + transactionId + '\'' +
                '}';
    }
}
