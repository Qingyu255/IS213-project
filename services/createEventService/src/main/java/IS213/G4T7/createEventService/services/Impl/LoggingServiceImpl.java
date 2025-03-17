package IS213.G4T7.createEventService.services.Impl;

import IS213.G4T7.createEventService.dto.LogMessage;
import IS213.G4T7.createEventService.services.LoggingService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.amqp.AmqpException;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

@Slf4j
@Service
public class LoggingServiceImpl implements LoggingService {

    private final RabbitTemplate rabbitTemplate;

    @Value("${rabbitmq.queue}")
    private String queueName;

    public LoggingServiceImpl(RabbitTemplate rabbitTemplate) {
        this.rabbitTemplate = rabbitTemplate;
    }

    public void sendLog(LogMessage logMessage) throws AmqpException {
        log.info("Attempting to send log message to RabbitMQ: {}", logMessage);
        rabbitTemplate.convertAndSend(queueName, logMessage);
        log.info("Sent log message to RabbitMQ: {}", logMessage);
    }
}
