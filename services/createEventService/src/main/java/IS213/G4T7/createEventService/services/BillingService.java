package IS213.G4T7.createEventService.services;

import IS213.G4T7.createEventService.dto.EventDetails;
import IS213.G4T7.createEventService.services.Impl.exceptions.BillingServiceException;


public interface BillingService {
    // TODO: return type is void for now but change when BillingService is complete
    public abstract boolean verifyEventCreationPaymentCompleted(EventDetails eventDetails) throws BillingServiceException;
}
