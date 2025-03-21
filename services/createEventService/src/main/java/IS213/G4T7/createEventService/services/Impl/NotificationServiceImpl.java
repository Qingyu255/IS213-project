package IS213.G4T7.createEventService.services.Impl;

import IS213.G4T7.createEventService.dto.AtomicServiceEventCreationResponse;
import IS213.G4T7.createEventService.dto.EmailData;
import IS213.G4T7.createEventService.services.Impl.exceptions.NotificationsServiceException;
import IS213.G4T7.createEventService.services.NotificationService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.List;

@Slf4j
@Service
public class NotificationServiceImpl implements NotificationService {

    @Value("${notifications.microservice.url}")
    private String notificationsMicroserviceUrl;

    private final RestTemplate restTemplate;

    public NotificationServiceImpl(RestTemplateBuilder restTemplateBuilder) {
        this.restTemplate = restTemplateBuilder.build();
    }

    public void sendSingleEmailNotification(EmailData emailData) throws NotificationsServiceException {
        //  TODO: Implement rest api call to Notifications Atomic service
        log.info("Attempting to send single email notification: {}", emailData);
        String url = notificationsMicroserviceUrl + "/SendEmail";
        try {
//            ResponseEntity<AtomicServiceEventCreationResponse> response = restTemplate.postForEntity(url, emailData, AtomicServiceEventCreationResponse.class);
//            log.info("Received response from notifications service. Status: {} | Body: {}", response.getStatusCode(), response.getBody());
//            log.info("Email notification sent successfully to: {}", emailData.getTo());
        } catch (Exception ex) {
            log.error("Exception occurred while sending email notification: {}", ex.getMessage(), ex);
            throw new NotificationsServiceException("Exception in sendSingleEmailNotification: " + ex.getMessage());
        }
    }

    public void sendBatchEmailNotification(List<EmailData> emailDataList) throws NotificationsServiceException {
        log.info("Starting batch email notifications for {} emails", emailDataList.size());
        for (EmailData emailData : emailDataList) {
            sendSingleEmailNotification(emailData);
        }
        log.info("Batch email notifications sent successfully for {} emails", emailDataList.size());
    }
}
