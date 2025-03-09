"use client";
import { useEffect, useRef } from "react";
import { Loader } from "@googlemaps/js-api-loader";

interface EventMapProps {
  center: { lat: number; lng: number };
  zoom: number;
  marker: { lat: number; lng: number };
}

export function EventMap({ center, zoom, marker }: EventMapProps) {
  const mapRef = useRef<HTMLDivElement>(null);
  const googleMapRef = useRef<google.maps.Map | null>(null);
  const markerRef = useRef<google.maps.Marker | null>(null);

  useEffect(() => {
    const initMap = async () => {
      const loader = new Loader({
        apiKey: process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY || "",
        version: "weekly",
      });

      // loader.load() will return the global google object
      await loader.load();

      if (mapRef.current) {
        googleMapRef.current = new google.maps.Map(mapRef.current, {
          center,
          zoom,
          styles: [
            {
              featureType: "all",
              elementType: "geometry",
              stylers: [{ color: "#242f3e" }],
            },
            {
              featureType: "all",
              elementType: "labels.text.stroke",
              stylers: [{ color: "#242f3e" }],
            },
            {
              featureType: "all",
              elementType: "labels.text.fill",
              stylers: [{ color: "#746855" }],
            },
            {
              featureType: "water",
              elementType: "geometry",
              stylers: [{ color: "#17263c" }],
            },
          ],
        });

        markerRef.current = new google.maps.Marker({
          position: marker,
          map: googleMapRef.current,
          title: "Event Location",
        });
      }
    };

    initMap();
  }, [center, zoom, marker]);

  return <div ref={mapRef} className="w-full h-full" />;
}
