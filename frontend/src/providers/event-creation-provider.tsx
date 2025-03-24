"use client"

import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react'
import type { EventDetails } from '@/types/event'

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
})

// Custom hook to use the context
export function useEventCreation() {
  return useContext(EventCreationContext)
}

// Provider component
export function EventCreationProvider({ children }: { children: ReactNode }) {
  const [eventData, setEventDataState] = useState<EventDetails | null>(null)
  const [initialized, setInitialized] = useState(false)

  // Initialize from localStorage on client-side mount
  useEffect(() => {
    console.log("PROVIDER: EventCreationProvider mounting");
    
    // Safety check for client-side code
    if (typeof window === 'undefined') {
      console.log("PROVIDER: Running on server, skipping localStorage check");
      return;
    }
    
    try {
      const storedData = localStorage.getItem('pending_event_data')
      
      if (!storedData) {
        console.log("PROVIDER: No event data found in localStorage during initialization");
        setInitialized(true);
        return;
      }
      
      console.log("PROVIDER: Found data in localStorage during initialization, length:", storedData.length);
      
      try {
        const parsedData = JSON.parse(storedData)
        console.log("PROVIDER: Successfully parsed event data from localStorage, ID:", parsedData.id);
        console.log("PROVIDER: Event title from localStorage:", parsedData.title);
        setEventDataState(parsedData)
      } catch (e) {
        console.error("PROVIDER: Error parsing localStorage data during initialization:", e)
        // If we can't parse the data, clear it to avoid future errors
        localStorage.removeItem('pending_event_data')
      }
    } catch (e) {
      console.error("PROVIDER: Error accessing localStorage during initialization:", e)
    } finally {
      setInitialized(true)
    }
  }, [])

  // Synchronize with localStorage when it changes elsewhere
  useEffect(() => {
    if (typeof window === 'undefined') return;
    
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'pending_event_data') {
        console.log("PROVIDER: localStorage event data changed externally");
        if (e.newValue) {
          try {
            const parsedData = JSON.parse(e.newValue);
            console.log("PROVIDER: Updating context from external localStorage change");
            setEventDataState(parsedData);
          } catch (err) {
            console.error("PROVIDER: Error parsing external localStorage change:", err);
          }
        } else {
          console.log("PROVIDER: External localStorage event data was cleared");
          setEventDataState(null);
        }
      }
    };
    
    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  const setEventData = (data: EventDetails) => {
    console.log("PROVIDER: Setting event data in context:", data.id);
    console.log("PROVIDER: Event title:", data.title);
    
    // Update state
    setEventDataState(data)
    
    // Sync with localStorage
    try {
      const jsonData = JSON.stringify(data);
      localStorage.setItem('pending_event_data', jsonData);
      
      // Verify storage worked
      const storedData = localStorage.getItem('pending_event_data');
      if (!storedData) {
        console.error("PROVIDER: Failed to store data in localStorage after verification check");
      } else {
        console.log("PROVIDER: Successfully stored event data in localStorage, verified");
      }
    } catch (e) {
      console.error("PROVIDER: Error storing event data in localStorage:", e)
    }
  }

  const clearEventData = () => {
    console.log("PROVIDER: Clearing event data from context and localStorage");
    setEventDataState(null)
    
    try {
      localStorage.removeItem('pending_event_data')
    } catch (e) {
      console.error("PROVIDER: Error removing event data from localStorage:", e)
    }
  }

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
  )
} 