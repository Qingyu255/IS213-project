import { EventDetails } from "@/types/event";
import { BACKEND_ROUTES } from "@/constants/backend-routes";
import { getBearerIdToken } from "@/utils/auth";

/**
 * Fetch a single event by ID
 */
export const getEventById = async (eventId: string): Promise<EventDetails> => {
  try {
    const response = await fetch(
      `${BACKEND_ROUTES.eventsService}/api/v1/events/${eventId}`,
      {
        method: "GET",
        headers: {
          Accept: "application/json",
          Authorization: await getBearerIdToken(),
        },
        mode: "cors",
        credentials: "omit",
      }
    );

    if (!response.ok) {
      throw new Error(`Error fetching event: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Error in getEventById:", error);
    throw error;
  }
};

/**
 * Update an existing event
 */
export const updateEvent = async (
  eventId: string,
  eventData: Partial<EventDetails>
): Promise<EventDetails> => {
  try {
    const response = await fetch(
      `${BACKEND_ROUTES.eventsService}/api/v1/events/update/${eventId}`,
      {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: await getBearerIdToken(),
        },
        body: JSON.stringify(eventData),
        mode: "cors",
        credentials: "omit",
      }
    );

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(
        errorData.message || `Error updating event: ${response.statusText}`
      );
    }

    return await response.json();
  } catch (error) {
    console.error("Error in updateEvent:", error);
    throw error;
  }
};

/**
 * Delete an event
 */
export const deleteEvent = async (eventId: string): Promise<void> => {
  try {
    const response = await fetch(
      `${BACKEND_ROUTES.eventsService}/api/v1/events/delete/${eventId}`,
      {
        method: "DELETE",
        headers: {
          Authorization: await getBearerIdToken(),
        },
        mode: "cors",
        credentials: "omit",
      }
    );

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData.message || `Error deleting event: ${response.statusText}`
      );
    }
  } catch (error) {
    console.error("Error in deleteEvent:", error);
    throw error;
  }
};

/**
 * Get events hosted by current user
 */
export const getUserHostedEvents = async (
  userId: string
): Promise<EventDetails[]> => {
  try {
    // First get all events
    const response = await fetch(`${BACKEND_ROUTES.eventsService}/api/v1/events/`,
      {
        method: "GET",
        headers: {
          Authorization: await getBearerIdToken(),
        },
      }
    );

    if (!response.ok) {
      throw new Error(`Error fetching events: ${response.statusText}`);
    }

    const allEvents = await response.json();

    // Filter events where the user is the organizer
    return allEvents.filter(
      (event: EventDetails) => event.organizer?.id === userId
    );
  } catch (error) {
    console.error("Error in getUserHostedEvents:", error);
    throw error;
  }
};
