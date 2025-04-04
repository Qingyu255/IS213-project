package IS213.G4T7.createEventService.services.utils;

import org.springframework.beans.factory.annotation.Value;

import IS213.G4T7.createEventService.dto.BasicUserData;
import IS213.G4T7.createEventService.dto.EmailData;

public class EmailTemplateEnricher {
    @Value("${frontend.url}")
    private static String frontendUrl;
    /**
     * Enriches an EmailData object with a fixed email template.
     * @param basicUserData User data to use for personalizing the email.
     * @param eventCategory The category of the event.
     * @return A populated EmailData object.
     */
    public static EmailData enrichEmailData(BasicUserData basicUserData, String eventCategory, String eventId) {
        EmailData emailData = new EmailData();

        // Set recipient email from BasicUserData; adjust getEmail() if needed.
        emailData.setEmail(basicUserData.getEmail());
        emailData.setSubject("Upcoming Event in " + eventCategory + " on Bookaroo!");

        // Create a fixed template with personalization
        String body = String.format(
                "We noticed that you have an interest in %s events. " +
                "There may be an upcoming event that matches your interests. " +
                "Check it out here: \n" +
                "%s \n" +
                "Best regards,\n" +
                "Event Service Team",
                basicUserData.getUsername(), eventCategory, frontendUrl + "/events/" + eventId
        );
        return emailData;
    }
}