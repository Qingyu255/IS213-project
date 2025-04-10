package IS213.G4T7.createEventService.services.Impl;

import java.util.List;

import org.springframework.beans.factory.annotation.Qualifier;
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

    public NotificationServiceImpl(@Qualifier("notificationRestTemplate") RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    public void sendSingleEmailNotification(EmailData emailData) throws NotificationsServiceException {
        log.info("Attempting to send single email notification: {}", emailData);
        // Validate email address is present
        if (emailData.getEmail() == null || emailData.getEmail().trim().isEmpty()) {
            String errorMsg = "Cannot send email: email address is null or empty";
            log.error(errorMsg);
            return;
        }

        String url = notificationsMicroserviceUrl + "/rest/confirmation/others";
        try {
            ResponseEntity<NotificationsServiceResponse> response = restTemplate.postForEntity(url, emailData,
                    NotificationsServiceResponse.class);
            log.info("Received response from notifications service. Status: {} | Body: {}", response.getStatusCode(),
                    response.getBody());

            if (!response.getBody().isSuccess()) {
                throw new NotificationsServiceException(response.getBody().getMessage());
            }

            log.info("Email notification sent successfully to: {}", emailData.getEmail());
        } catch (Exception ex) {
            log.error("Exception occurred while sending email notification: {}", ex.getMessage(), ex);
            throw new NotificationsServiceException("Exception in sendSingleEmailNotification: " + ex.getMessage());
        }
    }

    public void sendBatchEmailNotification(List<EmailData> emailDataList) throws NotificationsServiceException {
        log.info("Starting batch email notifications for {} emails", emailDataList.size());

        if (emailDataList == null || emailDataList.isEmpty()) {
            log.warn("Email data list is null or empty, no emails to send");
            return;
        }

        int successCount = 0;
        for (EmailData emailData : emailDataList) {
            try {
                sendSingleEmailNotification(emailData);
                successCount++;
            } catch (NotificationsServiceException e) {
                log.error("Failed to send email to {}: {}", emailData.getEmail(), e.getMessage());
            }
        }

        log.info("Batch email notifications completed. Successfully sent {}/{} emails",
                successCount, emailDataList.size());
    }
}
