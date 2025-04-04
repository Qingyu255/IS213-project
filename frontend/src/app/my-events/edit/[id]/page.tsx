"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Spinner } from "@/components/ui/spinner";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { ErrorMessageCallout } from "@/components/error-message-callout";
import { getEventById, updateEvent } from "@/lib/api/events";
import { ImageUploader } from "@/components/image-upload/image-uploader";

export default function EditEventPage() {
  const router = useRouter();
  const params = useParams();
  const eventId = params.id as string;

  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form state
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [venue, setVenue] = useState("");
  const [price, setPrice] = useState(0);
  const [capacity, setCapacity] = useState(0);
  const [imageUrl, setImageUrl] = useState("");
  const [address, setAddress] = useState("");
  const [city, setCity] = useState("");
  const [state, setState] = useState("");
  const [coordinates, setCoordinates] = useState<{ lat: number; lng: number }>({
    lat: 0,
    lng: 0,
  });
  const [additionalDetails, setAdditionalDetails] = useState("");
  const [startDateTime, setStartDateTime] = useState("");
  const [endDateTime, setEndDateTime] = useState("");

  useEffect(() => {
    async function fetchEvent() {
      try {
        setLoading(true);
        const eventData = await getEventById(eventId);

        // Set form values
        setTitle(eventData.title);
        setDescription(eventData.description || "");
        setVenue(eventData.venue?.name || "");
        setAddress(eventData.venue?.address || "");
        setCity(eventData.venue?.city || "");
        setState(eventData.venue?.state || "");
        setAdditionalDetails(eventData.venue?.additionalDetails || "");

        if (eventData.venue?.coordinates) {
          setCoordinates(eventData.venue.coordinates);
        }

        setPrice(eventData.price || 0);
        setCapacity(eventData.capacity || 0);
        setImageUrl(eventData.imageUrl || "/eventplaceholder.png");

        // Format dates for datetime-local input
        const startDate = new Date(eventData.startDateTime);
        const endDate = eventData.endDateTime
          ? new Date(eventData.endDateTime)
          : null;

        setStartDateTime(formatDateForInput(startDate));
        setEndDateTime(endDate ? formatDateForInput(endDate) : "");
      } catch (err) {
        console.error("Error fetching event:", err);
        setError(
          err instanceof Error ? err.message : "Failed to load event details"
        );
      } finally {
        setLoading(false);
      }
    }

    if (eventId) {
      fetchEvent();
    }
  }, [eventId]);

  const formatDateForInput = (date: Date) => {
    return date.toISOString().slice(0, 16);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      setUpdating(true);
      setError(null);

      const updatedEvent = {
        title,
        description,
        price: Number(price),
        capacity: Number(capacity),
        imageUrl,
        venue: {
          name: venue,
          address,
          city,
          state,
          additionalDetails,
          coordinates,
        },
        startDateTime: new Date(startDateTime).toISOString(),
        endDateTime: endDateTime
          ? new Date(endDateTime).toISOString()
          : undefined,
      };

      await updateEvent(eventId, updatedEvent);

      toast.success("Event updated successfully");
      router.push("/my-events");
    } catch (err) {
      console.error("Error updating event:", err);
      setError(err instanceof Error ? err.message : "Failed to update event");
      toast.error("Failed to update event");
    } finally {
      setUpdating(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Spinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <ErrorMessageCallout errorMessage={error} />
        <Button className="mt-4" onClick={() => router.back()}>
          Go Back
        </Button>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <Button variant="outline" className="mb-4" onClick={() => router.back()}>
        Back
      </Button>

      <Card className="w-full max-w-2xl mx-auto">
        <CardHeader>
          <CardTitle>Edit Event</CardTitle>
          <CardDescription>Update your event details</CardDescription>
        </CardHeader>

        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-6">
            {/* Image Uploader Component */}
            <ImageUploader
              initialImageUrl={imageUrl}
              onImageUploaded={(url) => setImageUrl(url)}
              label="Event Image"
              height="300px"
            />

            <div className="space-y-2">
              <Label htmlFor="title">Title</Label>
              <Input
                id="title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={4}
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="venue">Venue</Label>
                <Input
                  id="venue"
                  value={venue}
                  onChange={(e) => setVenue(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="address">Address</Label>
                <Input
                  id="address"
                  value={address}
                  onChange={(e) => setAddress(e.target.value)}
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="city">City</Label>
                <Input
                  id="city"
                  value={city}
                  onChange={(e) => setCity(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="state">State/Province</Label>
                <Input
                  id="state"
                  value={state}
                  onChange={(e) => setState(e.target.value)}
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="price">Price (SGD)</Label>
                <Input
                  id="price"
                  type="number"
                  min="0"
                  step="0.01"
                  value={price}
                  onChange={(e) => setPrice(parseFloat(e.target.value))}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="capacity">Capacity</Label>
                <Input
                  id="capacity"
                  type="number"
                  min="0"
                  value={capacity}
                  onChange={(e) => setCapacity(parseInt(e.target.value))}
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="startDateTime">Start Date & Time</Label>
                <Input
                  id="startDateTime"
                  type="datetime-local"
                  value={startDateTime}
                  onChange={(e) => setStartDateTime(e.target.value)}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="endDateTime">End Date & Time</Label>
                <Input
                  id="endDateTime"
                  type="datetime-local"
                  value={endDateTime}
                  onChange={(e) => setEndDateTime(e.target.value)}
                />
              </div>
            </div>
          </CardContent>

          <CardFooter className="flex justify-between">
            <Button
              variant="outline"
              type="button"
              onClick={() => router.back()}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={updating}>
              {updating ? <Spinner className="mr-2" size="sm" /> : null}
              Update Event
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
