package IS213.G4T7.createEventService.controllers;

import IS213.G4T7.createEventService.dto.LogMessage;
import IS213.G4T7.createEventService.models.CreateEventResponse;
import IS213.G4T7.createEventService.services.Impl.BillingServiceImpl;
import IS213.G4T7.createEventService.services.Impl.EventManagementServiceImpl;
import IS213.G4T7.createEventService.services.Impl.LoggingServiceImpl;
import IS213.G4T7.createEventService.services.Impl.NotificationServiceImpl;
import lombok.extern.slf4j.Slf4j;
import org.springframework.amqp.AmqpException;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@Slf4j
@RestController
@RequestMapping("/api/v1")
public class CreateEventController {

    private final EventManagementServiceImpl eventManagementServiceImpl;
    private final LoggingServiceImpl loggingServiceImpl;
//    private final BillingServiceImpl billingServiceImpl;
//    private final NotificationServiceImpl notificationServiceImpl;

    public CreateEventController(
            EventManagementServiceImpl eventManagementServiceImpl,
            LoggingServiceImpl loggingServiceImpl
    ) {
        this.eventManagementServiceImpl = eventManagementServiceImpl;
        this.loggingServiceImpl = loggingServiceImpl;
    }

    @PostMapping("/create-event")
    public ResponseEntity<CreateEventResponse> createEvent() {
        try {
            LogMessage testLogMessage = new LogMessage("createEventService", "info", "testing", "fake_id");
            loggingServiceImpl.sendLog(testLogMessage);
            CreateEventResponse response = new CreateEventResponse("Success");
            return ResponseEntity.ok(response);

        } catch (AmqpException ae) {
            String error = "Error creating event: " + ae.getMessage();
            log.error(error);
            CreateEventResponse response = new CreateEventResponse("Event Creation Failed", error);
            return ResponseEntity.badRequest().body(response);
        } catch (Exception e) {
            String error = "An unexpected exception occurred: " + e.getMessage();
            log.error(error);
            CreateEventResponse response = new CreateEventResponse("Event Creation Failed", error);
            return ResponseEntity.badRequest().body(response);
        }

    }

}
