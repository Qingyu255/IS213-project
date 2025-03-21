package IS213.G4T7.createEventService.services;

import IS213.G4T7.createEventService.services.Impl.exceptions.BroadcastingServiceException;

public interface BroadcastingService {
    public abstract void broadcastEventToUsersInterestedInCategory(String eventCategory, String eventId) throws BroadcastingServiceException;
}
