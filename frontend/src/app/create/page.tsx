"use client"
import { useEffect, useState, type FormEvent } from "react"
import type React from "react"

import Image from "next/image"
import { Calendar as CalendarIcon, Clock, ChevronDown, Users, Pencil, Ticket, Plus, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Textarea } from "@/components/ui/textarea"
import { Spinner } from "@/components/ui/spinner"
import { Calendar } from "@/components/ui/calendar"
import { useRouter } from "next/navigation"

import { fetchAuthSession } from "aws-amplify/auth"
import { Route } from "@/enums/Route"
import { InterestCategory } from "@/enums/InterestCategory"
import type { EventDetails } from "@/types/event"
import { toast } from "sonner"
import { BACKEND_ROUTES } from "@/constants/backend-routes"
import { getBearerToken } from "@/utils/auth"
import VenueAutocomplete from "@/components/googlemaps/VenueAutocomplete"
import useAuthUser from "@/hooks/use-auth-user"
import { ErrorMessageCallout } from "@/components/error-message-callout"
import { getErrorStringFromResponse } from "@/utils/common"

export default function CreateEventPage() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  // -----------------------
  // Form field states
  // -----------------------
  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [startDate, setStartDate] = useState("")
  const [startTime, setStartTime] = useState("")
  const [endDate, setEndDate] = useState("")
  const [endTime, setEndTime] = useState("")

  const [categories, setCategories] = useState<InterestCategory[]>([]);
  // const [eventType, setEventType] = useState<string>("public")
  const [amount, setAmount] = useState(0)
  const [currency, setCurrency] = useState("SGD")

  const [capacity, setCapacity] = useState<number | null>(null)
  const [isUnlimited, setIsUnlimited] = useState(true)

  // For image uploading: store multiple images
  const [images, setImages] = useState<string[]>(["/eventplaceholder.png"])
  const [mainImageIndex, setMainImageIndex] = useState(0)

  const [address, setAddress] = useState("");
  const [city, setCity] = useState("");
  const [stateValue, setStateValue] = useState("");
  const [venueName, setVenueName] = useState("");
  const [additionalDetails, setAdditionalDetails] = useState("");
  const [coordinates, setCoordinates] = useState<{ lat: number; lng: number }>({ lat: 0, lng: 0 });

  // Other fields
  const [timezone, setTimezone] = useState("utc")

  // -----------------------
  // Auth check on mount (DO NOT MODIFY)
  // -----------------------
  useEffect(() => {
    async function checkSession() {
      try {
        const session = await fetchAuthSession()
        const token = session.tokens?.accessToken
        if (!token) {
          router.replace(Route.Login)
        } else {
          setIsLoading(false)
        }
      } catch (err) {
        console.error("Session check failed:", err)
        router.replace(Route.Login)
      }
    }
    checkSession()
  }, [router])

  // Get authenticated user details
  const { user, getUserId } = useAuthUser();

  // -----------------------
  // Handle image file change
  // -----------------------
  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0]

      // Create a FileReader to encode the image as base64
      const reader = new FileReader()
      reader.onloadend = () => {
        const newImages = [...images]
        if (newImages[0] === "/placeholder.svg?height=200&width=200" && newImages.length === 1) {
          // Replace placeholder with actual image
          newImages[0] = reader.result as string
        } else {
          // Add new image
          newImages.push(reader.result as string)
        }
        setImages(newImages)
        setMainImageIndex(newImages.length - 1)
      }
      reader.readAsDataURL(file)
    }
  }

  // Remove an image
  function removeImage(index: number) {
    const newImages = [...images]
    newImages.splice(index, 1)

    // If we removed all images, add a placeholder back
    if (newImages.length === 0) {
      newImages.push("/placeholder.svg?height=200&width=200")
    }

    // Update main image index if needed
    if (index === mainImageIndex) {
      setMainImageIndex(0)
    } else if (index < mainImageIndex) {
      setMainImageIndex(mainImageIndex - 1)
    }

    setImages(newImages)
  }

  // Set an image as the main image
  function setAsMainImage(index: number) {
    setMainImageIndex(index)
  }

  // -----------------------
  // Submit Handler
  // -----------------------
  async function handleCreateEvent(e: FormEvent) {
    e.preventDefault()
    setSubmitting(true)
    setError(null)

    try {
      // Combine date and time for ISO 8601 strings
      const startDateTime = startDate && startTime ? new Date(`${startDate}T${startTime}`).toISOString() : ""
      const endDateTime = endDate && endTime ? new Date(`${endDate}T${endTime}`).toISOString() : undefined

      // Construct the event payload per our EventDetails type
      const newEvent: EventDetails = {
        id: "", // Backend will auto-generate the ID
        title,
        description,
        startDateTime: startDateTime,
        endDateTime: endDateTime,
        venue: {
          address: address,
          name: venueName,
          city: city,
          state: stateValue,
          coordinates: coordinates,
          additionalDetails: additionalDetails
        },
        imageUrl: images[mainImageIndex], // Use the main image (Note that additional images wont be posted to backend for now) and this is not working (explore s3 if there is time)
        categories,
        price: amount,
        organizer: {
          id: getUserId(), // e.g. the user's Cognito sub / user name; idt sub is the same as uuid in db
          username: (user && user.username) ? user.username : "",
        },
        capacity: isUnlimited ? undefined : (capacity ?? undefined),
      }

      // Send the payload to your backend
      const response = await fetch(`${BACKEND_ROUTES.createEventServiceUrl}/api/v1/create-event`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: await getBearerToken(),
        },
        body: JSON.stringify(newEvent),
      })

      if (!response.ok) {
        throw new Error(await getErrorStringFromResponse(response));
      }

      toast("Event created successfully!")

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (err: any) {
      console.error("Error creating event:", err)
      setError(err.message || "An unknown error occurred.")
    } finally {
      setSubmitting(false)
    }
  }

  // -----------------------
  // Render
  // -----------------------
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Spinner />
      </div>
    )
  }

  return (
    <div className="min-h-screen">
      <form onSubmit={handleCreateEvent} className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto">
          {/* HEADER IMAGE WITH FILE UPLOAD */}
          <div className="mb-8 space-y-4">
            {/* Main image display */}
            <div className="relative min-h-[400px] max-h-[700px] bg-primary-foreground dark:bg-secondary border border-1 rounded-lg">
              <Image
                src={images[mainImageIndex] || "/placeholder.svg"}
                alt="Event Image"
                fill
                className="rounded-lg object-contain"
                />
              <Button
                variant="outline"
                className="absolute bottom-4 right-4"
                type="button"
                onClick={() => {
                  // Trigger the hidden file input click
                  const fileInput = document.getElementById("image-upload")
                  if (fileInput) fileInput.click()
                }}
              >
                <Plus className="mr-2 h-4 w-4" />
                Add Image
              </Button>
              <input id="image-upload" type="file" accept="image/*" className="hidden" onChange={handleFileChange} />
            </div>
            {/* Image thumbnails */}
            {images.length > 0 && (
              <div className="flex flex-row flex-wrap gap-2 sm:flex-nowrap overflow-x-auto pb-2">
                {images.map((img, index) => (
                  <div
                    key={index}
                    className={`relative h-20 w-20 flex-shrink-0 cursor-pointer rounded-md overflow-hidden border-2 ${
                      index === mainImageIndex ? "border-primary" : "border-border"
                    }`}
                    onClick={() => setAsMainImage(index)}
                  >
                    <Image
                      src={img || "/placeholder.svg"}
                      alt={`Event Image ${index + 1}`}
                      fill
                      className="object-cover"
                    />
                    <Button
                      variant="destructive"
                      size="icon"
                      className="absolute top-0 right-0 h-5 w-5 rounded-full p-0"
                      onClick={(e) => {
                        e.stopPropagation()
                        removeImage(index)
                      }}
                    >
                      <X className="h-3 w-3" />
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* FORM FIELDS */}
          <div className="space-y-6">
            {/* Event Name */}
            <Input
              type="text"
              placeholder="Event Name"
              style={{ fontSize: "2.5rem" }}
              className="font-bold bg-transparent border-0 shadow-none h-16"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />

            {/* Description */}
            <div className="space-y-2">
              <Label className="font-bold">Description:</Label>
              <Textarea
                placeholder="Add Description"
                style={{ fontSize: "1.25rem" }}
                className="w-full min-h-[100px] p-3 font-semibold"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>

            {/* Date / Time */}
            <div className="space-y-2">
              <Label>Start Date & Time</Label>
              <div className="flex flex-col sm:flex-row gap-4">
                <Popover>
                  <PopoverTrigger asChild>
                    <Button variant="outline" className="w-full justify-start text-left font-normal">
                      <CalendarIcon className="mr-2 h-4 w-4" />
                      {startDate ? startDate : <span>Pick a date</span>}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0">
                    <Calendar
                      mode="single"
                      selected={startDate ? new Date(startDate) : undefined}
                      onSelect={(date) => date && setStartDate(date.toISOString().split("T")[0])}
                      disabled={{ before: new Date() }} // disables all dates before today
                      initialFocus
                    />
                  </PopoverContent>
                </Popover>
                <Popover>
                  <PopoverTrigger asChild>
                    <Button variant="outline" className="w-full justify-start text-left font-normal">
                      <Clock className="mr-2 h-4 w-4" />
                      {startTime ? startTime : <span>Set time</span>}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-4">
                    <div className="grid gap-2">
                      <div className="grid grid-cols-2 gap-2">
                        <Select
                          value={startTime.split(":")[0] || "12"}
                          onValueChange={(value) => {
                            // eslint-disable-next-line @typescript-eslint/no-unused-vars
                            const [_, minutes] = startTime.split(":")
                            setStartTime(`${value}:${minutes || "00"}`)
                          }}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Hour" />
                          </SelectTrigger>
                          <SelectContent>
                            {Array.from({ length: 24 }).map((_, i) => (
                              <SelectItem key={i} value={i.toString().padStart(2, "0")}>
                                {i.toString().padStart(2, "0")}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        <Select
                          value={startTime.split(":")[1] || "00"}
                          onValueChange={(value) => {
                            const [hours] = startTime.split(":")
                            setStartTime(`${hours || "12"}:${value}`)
                          }}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Minute" />
                          </SelectTrigger>
                          <SelectContent>
                            {Array.from({ length: 12 }).map((_, i) => (
                              <SelectItem key={i} value={(i * 5).toString().padStart(2, "0")}>
                                {(i * 5).toString().padStart(2, "0")}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                  </PopoverContent>
                </Popover>
              </div>
            </div>

            <div className="space-y-2">
              <Label>End Date & Time (Optional)</Label>
              <div className="flex flex-col sm:flex-row gap-4">
                <Popover>
                  <PopoverTrigger asChild>
                    <Button variant="outline" className="w-full justify-start text-left font-normal">
                      <CalendarIcon className="mr-2 h-4 w-4" />
                      {endDate ? endDate : <span>Pick a date</span>}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0">
                    <Calendar
                      mode="single"
                      selected={endDate ? new Date(endDate) : undefined}
                      onSelect={(date) => date && setEndDate(date.toISOString().split("T")[0])}
                      disabled={{ before: new Date() }}
                      initialFocus
                    />
                  </PopoverContent>
                </Popover>

                <Popover>
                  <PopoverTrigger asChild>
                    <Button variant="outline" className="w-full justify-start text-left font-normal">
                      <Clock className="mr-2 h-4 w-4" />
                      {endTime ? endTime : <span>Set time</span>}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-4">
                    <div className="grid gap-2">
                      <div className="grid grid-cols-2 gap-2">
                        <Select
                          value={endTime.split(":")[0] || "12"}
                          onValueChange={(value) => {
                            // eslint-disable-next-line @typescript-eslint/no-unused-vars
                            const [_, minutes] = endTime.split(":")
                            setEndTime(`${value}:${minutes || "00"}`)
                          }}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Hour" />
                          </SelectTrigger>
                          <SelectContent>
                            {Array.from({ length: 24 }).map((_, i) => (
                              <SelectItem key={i} value={i.toString().padStart(2, "0")}>
                                {i.toString().padStart(2, "0")}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        <Select
                          value={endTime.split(":")[1] || "00"}
                          onValueChange={(value) => {
                            const [hours] = endTime.split(":")
                            setEndTime(`${hours || "12"}:${value}`)
                          }}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Minute" />
                          </SelectTrigger>
                          <SelectContent>
                            {Array.from({ length: 12 }).map((_, i) => (
                              <SelectItem key={i} value={(i * 5).toString().padStart(2, "0")}>
                                {(i * 5).toString().padStart(2, "0")}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                  </PopoverContent>
                </Popover>
              </div>
            </div>

            {/* Timezone */}
            <Popover>
              <PopoverTrigger asChild>
                <Button variant="outline" className="w-full justify-between">
                  GMT+00:00 {timezone.toUpperCase()}
                  <ChevronDown className="ml-2 h-4 w-4 opacity-50" />
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-full p-0">
                <div className="grid gap-4 p-4">
                  <div className="space-y-2">
                    <h4 className="font-medium leading-none">Timezone</h4>
                    <p className="text-sm">Set the timezone for your event.</p>
                  </div>
                  <Select onValueChange={(val) => setTimezone(val)} defaultValue={timezone}>
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Select timezone" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="utc">GMT+00:00 UTC</SelectItem>
                      <SelectItem value="est">GMT-05:00 EST</SelectItem>
                      <SelectItem value="pst">GMT-08:00 PST</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </PopoverContent>
            </Popover>

           {/* Event Categories */}
            <div className="space-y-2">
              <Label className="font-bold">Event Categories:</Label>
              <Popover>
                <PopoverTrigger asChild>
                  <Button variant="outline" className="w-full text-left">
                    {categories.length > 0 ? categories.join(", ") : "Select categories"}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-80 p-4">
                  <div className="grid gap-2">
                    {Object.values(InterestCategory).map((cat) => (
                      <div key={cat} className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          id={`cat-${cat}`}
                          value={cat}
                          checked={categories.includes(cat)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setCategories((prev) => [...prev, cat]);
                            } else {
                              setCategories((prev) => prev.filter((c) => c !== cat));
                            }
                          }}
                          className="w-4 h-4"
                        />
                        <Label htmlFor={`cat-${cat}`}>{cat}</Label>
                      </div>
                    ))}
                  </div>
                </PopoverContent>
              </Popover>
            </div>

            {/* Visibility */}
            {/* <div className="space-y-2">
              <Label className="font-bold">Event Type:</Label>
              <Select onValueChange={(val) => setEventType(val)} defaultValue={eventType}>
                <SelectTrigger>
                  <SelectValue placeholder="Visibility" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="public">Public</SelectItem>
                  <SelectItem value="private">Private</SelectItem>
                </SelectContent>
              </Select>
            </div> */}
            <div className="space-y-2">
              <Label className="font-bold">Venue:</Label>
              <VenueAutocomplete
                address={address}
                setAddress={setAddress}
                setCity={setCity}
                setState={setStateValue}
                setVenueName={setVenueName}
                setAdditionalDetails={setAdditionalDetails}
                setCoordinates={setCoordinates}
              />
            </div>
            {/* Price & Options */}
            <div className="space-y-4 mt-8">
              <h2 className="text-xl font-semibold">Event Options</h2>
              <div className="space-y-4 border rounded-lg p-4">
                {/* Price */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Ticket className="h-5 w-5" />
                    <span>Price</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span>{amount > 0 ? `${amount} ${currency}` : "Free"}</span>
                    <Popover>
                      <PopoverTrigger asChild>
                        <Button variant="ghost" size="icon">
                          <Pencil className="h-4 w-4" />
                        </Button>
                      </PopoverTrigger>
                      <PopoverContent className="w-80">
                        <div className="grid gap-4">
                          <div className="space-y-2">
                            <h4 className="font-medium leading-none">Price</h4>
                            <p className="text-sm text-muted-foreground">Set the price for your event.</p>
                          </div>
                          <div className="grid grid-cols-2 gap-2">
                            <Input
                              type="number"
                              placeholder="0"
                              value={amount}
                              onChange={(e) => setAmount(Number.parseFloat(e.target.value) || 0)}
                            />
                            <Select value={currency} onValueChange={setCurrency}>
                              <SelectTrigger>
                                <SelectValue placeholder="Currency" />
                              </SelectTrigger>
                              <SelectContent>
                                {/* If need other currencies, backend will need refactoring as ems does not take in currency, assume all prices in sgd*/}
                                <SelectItem value="SGD">SGD</SelectItem>
                              </SelectContent>
                            </Select>
                          </div>
                        </div>
                      </PopoverContent>
                    </Popover>
                  </div>
                </div>

                {/* Capacity */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Users className="h-5 w-5" />
                    <span>Capacity</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span>{isUnlimited ? "Unlimited" : (capacity ?? 0)}</span>
                    <Popover>
                      <PopoverTrigger asChild>
                        <Button variant="ghost" size="icon">
                          <Pencil className="h-4 w-4" />
                        </Button>
                      </PopoverTrigger>
                      <PopoverContent className="w-80">
                        <div className="grid gap-4">
                          <div className="space-y-2">
                            <h4 className="font-medium leading-none">Capacity</h4>
                            <p className="text-sm text-muted-foreground">Set the maximum number of attendees.</p>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Switch id="unlimited-capacity" checked={isUnlimited} onCheckedChange={setIsUnlimited} />
                            <Label htmlFor="unlimited-capacity">Unlimited</Label>
                          </div>
                          {!isUnlimited && (
                            <Input
                              type="number"
                              placeholder="Number of spots"
                              value={capacity ?? ""}
                              onChange={(e) => setCapacity(Number.parseInt(e.target.value, 10) || 0)}
                            />
                          )}
                        </div>
                      </PopoverContent>
                    </Popover>
                  </div>
                </div>
              </div>
            </div>

            {/* Error Display */}
            {error && (
              <div className="p-4">
                <ErrorMessageCallout errorMessage={error} />
              </div>
            )}

            {/* Submit Button */}
            <Button className="w-full" type="submit" disabled={submitting}>
              {submitting ? "Creating..." : "Create Event"}
            </Button>
          </div>
        </div>
      </form>
    </div>
  )
}

