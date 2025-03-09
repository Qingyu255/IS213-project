"use client";
import { useEffect, useRef } from "react";
import { Input } from "@/components/ui/input";

type VenueAutocompleteProps = {
  address: string;
  setAddress: (addr: string) => void;
  setCity: (city: string) => void;
  setState: (state: string) => void;
  setVenueName: (name: string) => void;
  setAdditionalDetails: (details: string) => void;
  setCoordinates: (coords: { lat: number; lng: number }) => void;
};

export default function VenueAutocomplete({
  address,
  setAddress,
  setCity,
  setState,
  setVenueName,
  setAdditionalDetails,
  setCoordinates,
}: VenueAutocompleteProps) {
  const inputRef = useRef<HTMLInputElement | null>(null);

  function parseAddressComponents(
    components: (google.maps.places.AddressComponent | google.maps.GeocoderAddressComponent)[]
  ): { city: string; state: string } {
    let city = "";
    let state = "";
    components.forEach((component) => {
      // Use 'any' here to safely access the properties.
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const comp = component as any;
      if (comp.types && comp.types.includes("locality")) {
        city = comp.long_name;
      }
      if (comp.types && comp.types.includes("administrative_area_level_1")) {
        state = comp.short_name;
      }
    });
    return { city, state };
  }
  

  useEffect(() => {
    if (!window.google || !window.google.maps) {
      console.error("Google Maps JS API is not loaded");
      return;
    }

    if (inputRef.current) {
      const autocomplete = new window.google.maps.places.Autocomplete(
        inputRef.current,
        {
          fields: ["address_components", "geometry", "formatted_address", "name"],
          // Allow both addresses and establishments in results
          types: ["geocode", "establishment"],
        }
      );

      autocomplete.addListener("place_changed", () => {
        const place = autocomplete.getPlace();
        if (!place.geometry || !place.geometry.location) return;

        const formattedAddress = place.formatted_address || "";
        setAddress(formattedAddress);

        const { city, state } = parseAddressComponents(
          place.address_components || []
        );
        setCity(city);
        setState(state);

        // Use the place's name as additional details if available
        setVenueName(place.name || "");

        const lat = place.geometry.location.lat();
        const lng = place.geometry.location.lng();
        setCoordinates({ lat, lng });
      });
    }
  }, [setAddress, setCity, setState, setVenueName, setAdditionalDetails, setCoordinates]);

  return (
    <>
        <Input
            ref={inputRef}
            type="text"
            placeholder="Search for venue (e.g. SMU)"
            value={address}
            onChange={(e) => setAddress(e.target.value)}
        />
        <Input
            type="text"
            placeholder="Additional details (e.g., Suite, Floor, etc.)"
            onChange={(e) => setAdditionalDetails(e.target.value)}
        />
    </>
  );
}
