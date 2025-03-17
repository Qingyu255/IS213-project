package IS213.G4T7.createEventService.services;

import IS213.G4T7.createEventService.dto.AtomicServiceEventCreationDetails;
import IS213.G4T7.createEventService.dto.AtomicServiceEventCreationResponse;
import IS213.G4T7.createEventService.services.Impl.exceptions.AtomicServiceEventCreationException;

public interface EventsService {
    public abstract AtomicServiceEventCreationResponse createEvent(AtomicServiceEventCreationDetails event) throws AtomicServiceEventCreationException;
}
