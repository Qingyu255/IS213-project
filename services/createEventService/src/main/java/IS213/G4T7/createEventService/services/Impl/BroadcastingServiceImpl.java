package IS213.G4T7.createEventService.services.Impl;

import IS213.G4T7.createEventService.dto.BasicUserData;
import IS213.G4T7.createEventService.dto.EmailData;
import IS213.G4T7.createEventService.services.BroadcastingService;
import IS213.G4T7.createEventService.services.Impl.exceptions.BroadcastingServiceException;
import IS213.G4T7.createEventService.services.Impl.exceptions.NotificationsServiceException;
import IS213.G4T7.createEventService.services.utils.EmailTemplateEnricher;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.ArrayList;
import java.util.List;

@Slf4j
@Service
public class BroadcastingServiceImpl implements BroadcastingService {

    @Value("${user-management.microservice.url}")
    private String userManagementMicroserviceUrl;

    private final RestTemplate restTemplate;
    private final NotificationServiceImpl notificationServiceImpl;

    public BroadcastingServiceImpl(NotificationServiceImpl notificationServiceImpl, RestTemplateBuilder restTemplateBuilder) {
        this.notificationServiceImpl = notificationServiceImpl;
        this.restTemplate = restTemplateBuilder.build();
    }

    public void broadcastEventToUsersInterestedInCategory(String eventCategory, String eventId) throws BroadcastingServiceException {

        log.info("Starting broadcast for eventCategory: {} and eventId: {}", eventCategory, eventId);

        // 1. Query userManagementService for all users interested in the eventCategory
        List<BasicUserData> usersInterestedInCategory = getUsersInterestedInCategory(eventCategory);
        log.info("Retrieved {} users interested in category: {}", usersInterestedInCategory.size(), eventCategory);

        if (usersInterestedInCategory.isEmpty()) {
            log.info("No users interested in category found for eventCategory: {}. returning...", eventCategory);
            return;
        }

        // 2. For each user, enrich the email template with their details
        List<EmailData> emailsToSend = new ArrayList<>();
        for (BasicUserData user : usersInterestedInCategory) {
            EmailData emailData = EmailTemplateEnricher.enrichEmailData(user, eventCategory, eventId);
            emailsToSend.add(emailData);
        }
        log.info("Prepared {} email notifications for broadcasting", emailsToSend.size());

        // 3. Send Email to each user using Notifications Service
        try {
            notificationServiceImpl.sendBatchEmailNotification(emailsToSend);
        } catch (NotificationsServiceException nse) {
            throw new BroadcastingServiceException("Broadcasting failed due to exception in notifications atomic service: " + nse.getMessage());
        }
    }

    private List<BasicUserData> getUsersInterestedInCategory (String eventCategory) throws BroadcastingServiceException {
        String url = userManagementMicroserviceUrl + "/api/userinterests/getusers/" + eventCategory;
        log.info("Fetching users interested in category: {} from URL: {}", eventCategory, url);

        try {
            ResponseEntity<List<BasicUserData>> response = restTemplate.exchange(
                    url,
                    HttpMethod.GET,
                    null,
                    new ParameterizedTypeReference<List<BasicUserData>>() {}
            );

            log.info("Received response with status: {}", response.getStatusCode());
            List<BasicUserData> users = response.getBody();
            log.info("Fetched {} users for category: {}", users != null ? users.size() : 0, eventCategory);
            return users;
        } catch (Exception ex) {
            log.error("Exception occurred while fetching users for category {}: {}", eventCategory, ex.getMessage(), ex);
            throw new BroadcastingServiceException("Exception in getUsersInterestedInCategory: " + ex.getMessage());
        }
    }
}
