package IS213.G4T7.createEventService.services;

import IS213.G4T7.createEventService.dto.LogMessage;

public interface LoggingService {
    public abstract void sendLog(LogMessage logMessage);
}
