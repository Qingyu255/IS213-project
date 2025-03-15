package IS213.G4T7.createEventService.controllers;

import IS213.G4T7.createEventService.services.EventManagementService;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/createEvent")
public class CreateEventController {
    private final EventManagementService eventManagementService;

    public CreateEventController(EventManagementService eventManagementService) {
        this.eventManagementService = eventManagementService;
    }



}
