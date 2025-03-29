/* eslint-disable @typescript-eslint/no-unused-vars */
"use client";

import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';
import type { EventDetails } from '@/types/event';

// Context type definition
interface EventCreationContextType {
  eventData: EventDetails | null
  setEventData: (data: EventDetails) => void
  clearEventData: () => void
}

// Create the context with default values
const EventCreationContext = createContext<EventCreationContextType>({
  eventData: null,
  setEventData: () => {},
  clearEventData: () => {}
});

// Custom hook to use the context
export function useEventCreation() {
  return useContext(EventCreationContext);
}

// Provider component
export function EventCreationProvider({ children }: { children: ReactNode }) {
  const [eventData, setEventDataState] = useState<EventDetails | null>(null);
  const [initialized, setInitialized] = useState(false);

  // Initialize from localStorage on client-side mount
  useEffect(() => {
    // Safety check for client-side code
    if (typeof window === 'undefined') return;
    
    try {
      // Try to restore from localStorage - this helps with page refreshes
      const storedData = localStorage.getItem('pending_event_data');
      
      if (!storedData) {
        setInitialized(true);
        return;
      }
      
      try {
        const parsedData = JSON.parse(storedData);
        console.log("Restored event data from localStorage, ID:", parsedData.id);
        
        // Set the data in our context
        setEventDataState(parsedData);
      } catch (e) {
        console.error("Error parsing saved data:", e);
        // If we can't parse the data, clear it to avoid future errors
        localStorage.removeItem('pending_event_data');
      }
    } catch (e) {
      console.error("Error during initialization:", e);
    } finally {
      setInitialized(true);
    }
  }, []);

  // Synchronize with localStorage when it changes elsewhere
  useEffect(() => {
    if (typeof window === 'undefined') return;
    
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'pending_event_data') {
        if (e.newValue) {
          try {
            const parsedData = JSON.parse(e.newValue);
            console.log("External storage change detected, updating context");
            setEventDataState(parsedData);
          } catch (err) {
            console.error("Error parsing external data change:", err);
          }
        } else {
          setEventDataState(null);
        }
      }
    };
    
    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  const setEventData = (data: EventDetails) => {
    console.log("Setting event data in context, ID:", data.id);
    
    // Update context state - this is the PRIMARY storage
    setEventDataState(data);
    
    // Sync with localStorage as backup
    try {
      localStorage.setItem('pending_event_data', JSON.stringify(data));
    } catch (e) {
      console.error("Error saving to localStorage:", e);
    }
  };

  const clearEventData = () => {
    // Clear primary storage (context)
    setEventDataState(null);
    
    // Also clear backup
    try {
      localStorage.removeItem('pending_event_data');
    } catch (e) {
      console.error("Error clearing localStorage:", e);
    }
  };

  return (
    <EventCreationContext.Provider
      value={{
        eventData,
        setEventData,
        clearEventData
      }}
    >
      {children}
    </EventCreationContext.Provider>
  );
} 