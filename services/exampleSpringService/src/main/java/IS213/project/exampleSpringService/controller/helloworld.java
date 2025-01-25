package IS213.project.exampleSpringService.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

// TODO: Setup logging
@RestController
@RequestMapping("/api")
public class helloworld {
    @GetMapping("/hellospring")
    public String index() {
        return "{\"message\": \"Hello from Spring Boot!\"}";
    }
}
