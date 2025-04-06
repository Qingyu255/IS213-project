package IS213.G4T7.createEventService.services.utils;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import IS213.G4T7.createEventService.dto.BasicUserData;
import IS213.G4T7.createEventService.dto.EmailData;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@Component
public class EmailTemplateEnricher {

    @Value("${frontend.url}")
    private String frontendUrl;

    /**
     * Enriches an EmailData object with a fixed email template.
     *
     * @param basicUserData User data to use for personalizing the email.
     * @param eventCategory The category of the event.
     * @return A populated EmailData object.
     */
    public EmailData enrichEmailData(BasicUserData basicUserData, String eventCategory, String eventId) {
        EmailData emailData = new EmailData();

        // Set recipient email from BasicUserData; adjust getEmail() if needed.
        emailData.setEmail(basicUserData.getEmail());
        emailData.setSubject("Upcoming Event in " + eventCategory + " on Bookaroo!");
        log.info("Preparing email for user: {}, email: {}", basicUserData.getUsername(), basicUserData.getEmail());

        // Create a fixed template with personalization
        String message = String.format(
                "%s, We noticed that you have an interest in %s events. " +
                        "There may be an upcoming event that matches your interests. " +
                        "Check it out here: \n" +
                        "%s/events/%s \n" +
                        "Best regards,\n" +
                        "Event Service Team",
                basicUserData.getUsername(), eventCategory, frontendUrl, eventId
        );
        emailData.setMainMessage(message);
        return emailData;
    }
}