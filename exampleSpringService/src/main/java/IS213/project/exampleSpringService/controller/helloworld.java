package IS213.project.exampleSpringService.controller;

import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/helloworld")
public class helloworld {
    @GetMapping("")
    public String index() {
        return "Greetings from Spring Boot!";
    }
}
