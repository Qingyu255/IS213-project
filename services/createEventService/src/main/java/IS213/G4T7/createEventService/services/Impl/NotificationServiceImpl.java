package IS213.G4T7.createEventService.services.Impl;

import java.util.List;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import IS213.G4T7.createEventService.dto.EmailData;
import IS213.G4T7.createEventService.dto.NotificationsServiceResponse;
import IS213.G4T7.createEventService.services.Impl.exceptions.NotificationsServiceException;
import IS213.G4T7.createEventService.services.NotificationService;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@Service
public class NotificationServiceImpl implements NotificationService {

    @Value("${notifications.microservice.url}")
    private String notificationsMicroserviceUrl;

    private final RestTemplate restTemplate;

    public NotificationServiceImpl(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    public void sendSingleEmailNotification(EmailData emailData) throws NotificationsServiceException {
        log.info("Attempting to send single email notification: {}", emailData);
        String url = notificationsMicroserviceUrl;
        try {
            ResponseEntity<NotificationsServiceResponse> response = restTemplate.postForEntity(url, emailData, NotificationsServiceResponse.class);
            log.info("Received response from notifications service. Status: {} | Body: {}", response.getStatusCode(), response.getBody());
            log.info("Email notification sent successfully to: {}", emailData.getEmail());
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
