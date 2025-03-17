package IS213.G4T7.createEventService.services;

import IS213.G4T7.createEventService.dto.EmailData;
import IS213.G4T7.createEventService.services.Impl.exceptions.NotificationsServiceException;

import java.util.List;

public interface NotificationService {
    public abstract void sendSingleEmailNotification(EmailData emailData) throws NotificationsServiceException;
    public abstract void sendBatchEmailNotification(List<EmailData> emailDataList) throws NotificationsServiceException;
}
