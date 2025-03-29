package IS213.G4T7.createEventService.controllers;

import IS213.G4T7.createEventService.dto.*;
import IS213.G4T7.createEventService.services.Impl.*;
import IS213.G4T7.createEventService.services.Impl.exceptions.AtomicServiceEventCreationException;
import IS213.G4T7.createEventService.services.Impl.exceptions.BillingServiceException;
import IS213.G4T7.createEventService.services.Impl.exceptions.BroadcastingServiceException;
import IS213.G4T7.createEventService.services.utils.EventMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@Slf4j
@RestController
@RequestMapping("/api/v1")
public class CreateEventController {

    private final BillingServiceImpl billingServiceImpl;
    private final EventsServiceImpl eventsServiceImpl;
    private final LoggingServiceImpl loggingServiceImpl;
    private final NotificationServiceImpl notificationServiceImpl;
    private final BroadcastingServiceImpl broadcastingServiceImpl;

    public CreateEventController(
            BillingServiceImpl billingServiceImpl,
            EventsServiceImpl eventsServiceImpl,
            LoggingServiceImpl loggingServiceImpl,
            NotificationServiceImpl notificationServiceImpl,
            BroadcastingServiceImpl broadcastingServiceImpl
    ) {
        this.eventsServiceImpl = eventsServiceImpl;
        this.loggingServiceImpl = loggingServiceImpl;
        this.billingServiceImpl = billingServiceImpl;
        this.notificationServiceImpl = notificationServiceImpl;
        this.broadcastingServiceImpl = broadcastingServiceImpl;
    }

    @PostMapping("/create-event")
    public ResponseEntity<CreateEventResponse> createEvent(@RequestBody EventDetails eventDetails) {
        String error = null;
        try {
            log.info("Received event creation request at /create-event for: " + eventDetails);
            LogMessage eventCreationRequestReceivedLogMessage = new LogMessage(
                    "info",
                    String.format("Received event details: %s", eventDetails)
            );
            log.info(eventCreationRequestReceivedLogMessage.toString()); // log at service level too
            loggingServiceImpl.sendLog(eventCreationRequestReceivedLogMessage);

            // 1. Check if paid with Atomic billing service
            boolean isEventCreationPaymentCompleted = billingServiceImpl.verifyEventCreationPaymentCompleted(eventDetails);
            if (!isEventCreationPaymentCompleted) {
                CreateEventResponse response = new CreateEventResponse(
                    "Event Creation Failed",
                    String.format("No payment has been made for the event creation of event title: %s", eventDetails.getTitle())
                );
                return ResponseEntity.ok(response);
            }

            // 2. Send to Events Atomic Microservice for event creation
            AtomicServiceEventCreationResponse atomicServiceEventCreationResponse = eventsServiceImpl.createEvent(EventMapper.toAtomic(eventDetails));

            // 3. Log successful event creation to logging service on event creation
            LogMessage eventCreationSuccessLogMessage = new LogMessage(
                "info",
                String.format("Created event with ID: %s", atomicServiceEventCreationResponse.getId()),
                atomicServiceEventCreationResponse.getId()
            );
            log.info(eventCreationSuccessLogMessage.toString());
            loggingServiceImpl.sendLog(eventCreationSuccessLogMessage);

            // 4. Broadcast Event to users interested in the event category via email (Notifications Service)
            for (String category : atomicServiceEventCreationResponse.getCategories()) {
                broadcastingServiceImpl.broadcastEventToUsersInterestedInCategory(category, atomicServiceEventCreationResponse.getId());
            }

            // 5. Log successful event broadcast to logging service on event creation
            LogMessage eventBroadCastSuccessLogMessage = new LogMessage(
                    "info",
                    String.format("Broadcasted event with ID:  %s to interested users successfully", atomicServiceEventCreationResponse.getId()),
                    atomicServiceEventCreationResponse.getId()
            );
            log.info(eventBroadCastSuccessLogMessage.toString());
            loggingServiceImpl.sendLog(eventBroadCastSuccessLogMessage);

            // 6. Send success email to the organizer
            Jwt jwt = (Jwt) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
            String organizerEmail = jwt.getClaimAsString("email");
            if (organizerEmail != null) {
                EmailData eventCreationOutcomeEmailData = new EmailData();
                eventCreationOutcomeEmailData.setEmail(organizerEmail);
                eventCreationOutcomeEmailData.setSubject("Event Creation Success - " + eventDetails.getTitle());
                String emailMessage = String.format(
                    "%s, your event '%s' has been successfully created!\n\n" +
                    "Event Details:\n" +
                    "- Title: %s\n" +
                    "- Start Date: %s\n" +
                    "- Categories: %s\n\n" +
                    "You can view and manage your event in your dashboard.\n\n" +
                    "Best regards,\n" +
                    "Mulan Event Team",
                    eventDetails.getOrganizer().getUsername(),
                    eventDetails.getTitle(),
                    eventDetails.getTitle(),
                    eventDetails.getStartDateTime(),
                    String.join(", ", eventDetails.getCategories())
                );
                eventCreationOutcomeEmailData.setMainMessage(emailMessage);
                notificationServiceImpl.sendSingleEmailNotification(eventCreationOutcomeEmailData);
                log.info("Sent success email to organizer: {}", organizerEmail);
            } else {
                log.warn("Could not find organizer email in JWT claims");
            }

            CreateEventResponse response = new CreateEventResponse("Success");

            return ResponseEntity.ok(response);

        } catch (BillingServiceException bse) {
            error = "BillingServiceException — Error verifying event creation payment with atomic service, Billing Service: " + bse.getMessage();
            CreateEventResponse response = new CreateEventResponse("Event Creation Failed", error);
            return ResponseEntity
                    .badRequest()
                    .body(response);
        } catch (AtomicServiceEventCreationException ece) {
            error = "AtomicServiceEventCreationException — Error creating event with atomic service, Events Service: " + ece.getMessage();
            CreateEventResponse response = new CreateEventResponse("Event Creation Failed", error);
            return ResponseEntity
                    .badRequest()
                    .body(response);
        } catch (BroadcastingServiceException bse) {
            error = "BroadcastingServiceException — Error Broadcasting to interested users: " + bse.getMessage();
            CreateEventResponse response = new CreateEventResponse("Event Creation Succeeded with errors", error); // so that users now that event created but broadcast failed
            return ResponseEntity
                    .internalServerError()
                    .body(response);
        } catch (Exception e) {
            error = "An unexpected exception occurred: " + e.getMessage();
            CreateEventResponse response = new CreateEventResponse("Event Creation Exception", error);
            return ResponseEntity
                    .internalServerError()
                    .body(response);
        } finally {
            // Log error at the end at service level and to logging service
            if (error != null) {
                log.error(error);
                LogMessage eventCreationRequestReceivedLogMessage = new LogMessage("error", error);
                loggingServiceImpl.sendLog(eventCreationRequestReceivedLogMessage);
            }
        }
    }
}
