"use client"
import { useEffect, useState, type FormEvent } from "react"
import type React from "react"
import { v4 as uuidv4 } from "uuid"

import Image from "next/image"
import {
  Calendar as CalendarIcon,
  Clock,
  ChevronDown,
  Users,
  Pencil,
  Ticket,
  Upload,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"
import { Textarea } from "@/components/ui/textarea"
import { Spinner } from "@/components/ui/spinner"
import { Calendar } from "@/components/ui/calendar"
import { useRouter, useSearchParams } from "next/navigation"

import { fetchAuthSession } from "aws-amplify/auth"
import { Route } from "@/enums/Route"
import { InterestCategory } from "@/enums/InterestCategory"
import type { EventDetails } from "@/types/event"
import { toast } from "sonner"
import VenueAutocomplete from "@/components/googlemaps/VenueAutocomplete"
import useAuthUser from "@/hooks/use-auth-user"
import { ErrorMessageCallout } from "@/components/error-message-callout"
import { useEventCreation } from "@/providers/event-creation-provider"

// Constants
const EVENT_CREATION_FEE_CENTS = 200 // $2.00 SGD

export default function CreateEventPage() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const { setEventData } = useEventCreation()

  // -----------------------
  // Form field states
  // -----------------------
  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [startDate, setStartDate] = useState("")
  const [startTime, setStartTime] = useState("")
  const [endDate, setEndDate] = useState("")
  const [endTime, setEndTime] = useState("")

  const [categories, setCategories] = useState<InterestCategory[]>([])
  const [amount, setAmount] = useState(0)
  const [currency, setCurrency] = useState("SGD")

  const [capacity, setCapacity] = useState<number | null>(null)
  const [isUnlimited, setIsUnlimited] = useState(true)

  const [imageUrl, setImageUrl] = useState<string>("/eventplaceholder.png")
  const [isUploading, setIsUploading] = useState(false)

  const [address, setAddress] = useState("")
  const [city, setCity] = useState("")
  const [stateValue, setStateValue] = useState("")
  const [venueName, setVenueName] = useState("")
  const [additionalDetails, setAdditionalDetails] = useState("")
  const [coordinates, setCoordinates] = useState<{ lat: number; lng: number }>({
    lat: 0,
    lng: 0,
  })

  // Other fields
  const [timezone, setTimezone] = useState("utc")

  const searchParams = useSearchParams()
  if (searchParams.get("canceled")) {
    console.log(
      "Event Creation Payment canceled"
      // route to cancelled page?
    )
  }
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
  const { user, getUserId } = useAuthUser()

  // -----------------------
  // Handle image file upload to S3
  // -----------------------
  async function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0]

      // Validate file type
      if (!file.type.startsWith("image/")) {
        toast.error("Please upload an image file")
        return
      }

      // Validate file size (5MB max)
      if (file.size > 5 * 1024 * 1024) {
        toast.error("Image size should be less than 5MB")
        return
      }

      try {
        setIsUploading(true)

        // Create FormData to send file
        const formData = new FormData()
        formData.append("file", file)

        console.log(
          `Uploading file: ${file.name}, size: ${file.size}, type: ${file.type}`
        )

        // Upload to S3 via our API route
        const response = await fetch("/api/upload", {
          method: "POST",
          body: formData,
        })

        // Log the response status for debugging
        console.log(`Upload response status: ${response.status}`)

        // Try to get response as text first for debugging
        const responseText = await response.text()
        console.log(`Response text: ${responseText}`)

        // Parse the response if it's valid JSON
        let data
        try {
          data = JSON.parse(responseText)
        } catch (jsonError) {
          console.error("Error parsing response as JSON:", jsonError)
          throw new Error("Invalid response format from server")
        }

        if (!response.ok) {
          throw new Error(
            data.error || `Upload failed with status: ${response.status}`
          )
        }

        if (!data.url) {
          throw new Error("No URL returned from server")
        }

        console.log(`File uploaded successfully. URL: ${data.url}`)
        setImageUrl(data.url)
        toast.success("Image uploaded successfully")
      } catch (err) {
        console.error("Image upload error:", err)
        toast.error(
          err instanceof Error ? err.message : "Failed to upload image"
        )
      } finally {
        setIsUploading(false)
      }
    }
  }

  // Helper function to convert to UTC
  function convertToUTC(date: Date, timezone: string): Date {
    const localDate = new Date(date)
    let offset = 0

    switch (timezone) {
      case "est":
        offset = 5 * 60 // EST is UTC-5
        break
      case "pst":
        offset = 8 * 60 // PST is UTC-8
        break
      case "utc":
      default:
        offset = 0
    }

    // Add the offset to convert to UTC
    return new Date(localDate.getTime() + offset * 60000)
  }

  // -----------------------
  // Submit Handler
  // -----------------------
  const eventUuid = uuidv4()
  async function handleCreateEvent(e: FormEvent) {
    e.preventDefault()
    setSubmitting(true)
    setError(null)

    try {
      // Validate start date and time
      if (!startDate || !startTime) {
        setError(
          "Please select both a start date and start time for your event"
        )
        setSubmitting(false)
        return
      }

      // Validate end date and time (if one is provided, both must be provided)
      if ((endDate && !endTime) || (!endDate && endTime)) {
        setError(
          "Please provide both end date and end time, or leave both empty"
        )
        setSubmitting(false)
        return
      }

      // Create Date objects from the selected date and time
      const startDateObj = new Date(`${startDate}T${startTime}`)
      const endDateObj =
        endDate && endTime ? new Date(`${endDate}T${endTime}`) : undefined

      // Validate that end datetime is after start datetime if provided
      if (endDateObj && endDateObj <= startDateObj) {
        setError("End date and time must be after the start date and time")
        setSubmitting(false)
        return
      }

      // Convert dates to UTC based on selected timezone
      const startDateTimeUTC = convertToUTC(startDateObj, timezone)
      const endDateTimeUTC = endDateObj
        ? convertToUTC(endDateObj, timezone)
        : undefined

      // Generate a proper UUID that's compatible with Java UUID format

      // Get the organizer ID (user ID)
      const organizerId = getUserId()

      // Construct the event payload per our EventDetails type
      const newEvent: EventDetails = {
        id: eventUuid,
        title,
        description,
        startDateTime: startDateTimeUTC.toISOString(),
        endDateTime: endDateTimeUTC?.toISOString(),
        venue: {
          address: address,
          name: venueName,
          city: city,
          state: stateValue,
          coordinates: coordinates,
          additionalDetails: additionalDetails,
        },
        imageUrl: imageUrl, // Use S3 image URL
        categories,
        price: amount,
        organizer: {
          id: organizerId,
          username: user && user.username ? user.username : "",
        },
        capacity: isUnlimited ? undefined : capacity ?? undefined,
      }

      // Store in context first
      setEventData(newEvent)

      // Also save in localStorage for redundancy
      try {
        localStorage.setItem("pending_event_data", JSON.stringify(newEvent))
        console.log("Stored event data in localStorage:", newEvent)
      } catch (err) {
        // Just log the error but continue - we're using context as primary
        console.warn("Failed to use localStorage as backup:", err)
      }

      // Create a payment session with Stripe
      const response = await fetch("/api/stripe", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          eventId: newEvent.id,
          organizerId: organizerId, // Include the organizer ID for verification
          amount: EVENT_CREATION_FEE_CENTS,
          description: `Event creation fee for "${newEvent.title}"`,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(
          `Error creating payment session: ${
            errorData.error || response.statusText
          }`
        )
      }

      const { url } = await response.json()

      if (!url) {
        throw new Error("No checkout URL returned from payment service")
      }

      // Redirect to the Stripe Checkout page
      window.location.href = url

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (err: any) {
      console.error("Error preparing event creation:", err)
      setError(err.message || "An unknown error occurred.")
      setSubmitting(false)
      // Show error toast
      toast.error(err.message || "An unknown error occurred.")
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
      <form
        onSubmit={handleCreateEvent}
        className="container mx-auto px-4 py-8"
      >
        <div className="max-w-2xl mx-auto">
          {/* HEADER IMAGE WITH FILE UPLOAD */}
          <div className="mb-8 space-y-4">
            <Label className="font-bold">Event Image</Label>
            {/* Main image display */}
            <div className="relative min-h-[400px] max-h-[700px] bg-primary-foreground dark:bg-secondary border border-1 rounded-lg">
              <Image
                src={imageUrl}
                alt="Event Image"
                fill
                className="rounded-lg object-contain"
              />
              <div className="absolute bottom-4 right-4 flex gap-2">
                <Button
                  variant="outline"
                  className="relative"
                  type="button"
                  disabled={isUploading}
                  onClick={() => {
                    // Trigger the hidden file input click
                    const fileInput = document.getElementById("image-upload")
                    if (fileInput) fileInput.click()
                  }}
                >
                  {isUploading ? (
                    <Spinner className="mr-2 h-4 w-4" />
                  ) : (
                    <Upload className="mr-2 h-4 w-4" />
                  )}
                  {isUploading ? "Uploading..." : "Upload Cover Image"}
                </Button>
                <input
                  id="image-upload"
                  type="file"
                  accept="image/*"
                  className="hidden"
                  onChange={handleFileChange}
                />
                <input
                  id="event-id"
                  type="text"
                  className="hidden"
                  defaultValue={eventUuid}
                />
              </div>
            </div>
            {/* Show the image URL in a smaller text below the image for verification */}
            {imageUrl !== "/eventplaceholder.png" && (
              <div className="mt-2">
                <p className="text-xs text-muted-foreground break-all">
                  {imageUrl.includes("s3.amazonaws.com") &&
                    "Image Uploaded successfully"}
                </p>
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
              <Label>
                Start Date & Time <span className="text-red-500">*</span>
              </Label>
              <div className="flex flex-col sm:flex-row gap-4">
                <Popover>
                  <PopoverTrigger asChild>
                    <Button
                      variant="outline"
                      className={`w-full justify-start text-left font-normal ${
                        !startDate ? "border-red-200 dark:border-red-800" : ""
                      }`}
                    >
                      <CalendarIcon className="mr-2 h-4 w-4" />
                      {startDate ? startDate : <span>Pick a date</span>}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0">
                    <Calendar
                      mode="single"
                      selected={startDate ? new Date(startDate) : undefined}
                      onSelect={(date) => {
                        if (date) {
                          // Adjust the date to account for timezone offset
                          const localDate = new Date(
                            date.getTime() - date.getTimezoneOffset() * 60000
                          )
                          setStartDate(localDate.toISOString().split("T")[0])
                        }
                      }}
                      disabled={{ before: new Date() }} // disables all dates before today
                      initialFocus
                    />
                  </PopoverContent>
                </Popover>
                <Popover>
                  <PopoverTrigger asChild>
                    <Button
                      variant="outline"
                      className={`w-full justify-start text-left font-normal ${
                        !startTime ? "border-red-200 dark:border-red-800" : ""
                      }`}
                    >
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
                              <SelectItem
                                key={i}
                                value={i.toString().padStart(2, "0")}
                              >
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
                              <SelectItem
                                key={i}
                                value={(i * 5).toString().padStart(2, "0")}
                              >
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
              <p className="text-sm text-muted-foreground">
                Both start date and time are required.
              </p>
            </div>

            {/* Rest of the form fields remain the same */}
            <div className="space-y-2">
              <Label>End Date & Time (Optional)</Label>
              <div className="flex flex-col sm:flex-row gap-4">
                <Popover>
                  <PopoverTrigger asChild>
                    <Button
                      variant="outline"
                      className={`w-full justify-start text-left font-normal ${
                        endTime && !endDate
                          ? "border-red-200 dark:border-red-800"
                          : ""
                      }`}
                    >
                      <CalendarIcon className="mr-2 h-4 w-4" />
                      {endDate ? endDate : <span>Pick a date</span>}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0">
                    <Calendar
                      mode="single"
                      selected={endDate ? new Date(endDate) : undefined}
                      onSelect={(date) => {
                        if (date) {
                          // Adjust the date to account for timezone offset
                          const localDate = new Date(
                            date.getTime() - date.getTimezoneOffset() * 60000
                          )
                          setEndDate(localDate.toISOString().split("T")[0])
                        }
                      }}
                      disabled={{ before: new Date() }}
                      initialFocus
                    />
                  </PopoverContent>
                </Popover>

                <Popover>
                  <PopoverTrigger asChild>
                    <Button
                      variant="outline"
                      className={`w-full justify-start text-left font-normal ${
                        endDate && !endTime
                          ? "border-red-200 dark:border-red-800"
                          : ""
                      }`}
                    >
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
                              <SelectItem
                                key={i}
                                value={i.toString().padStart(2, "0")}
                              >
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
                              <SelectItem
                                key={i}
                                value={(i * 5).toString().padStart(2, "0")}
                              >
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
              <p className="text-sm text-muted-foreground">
                If setting an end time, both date and time must be provided. End
                time must be after start time.
              </p>
            </div>

            {/* Timezone */}
            <Popover>
              <PopoverTrigger asChild>
                <Button variant="outline" className="w-full justify-between">
                  {timezone === "utc"
                    ? "GMT+00:00 UTC"
                    : timezone === "est"
                    ? "GMT-05:00 EST"
                    : "GMT-08:00 PST"}
                  <ChevronDown className="ml-2 h-4 w-4 opacity-50" />
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-full p-0">
                <div className="grid gap-4 p-4">
                  <div className="space-y-2">
                    <h4 className="font-medium leading-none">Timezone</h4>
                    <p className="text-sm">Set the timezone for your event.</p>
                  </div>
                  <Select
                    onValueChange={(val) => setTimezone(val)}
                    value={timezone}
                  >
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
                    {categories.length > 0
                      ? categories.join(", ")
                      : "Select categories"}
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
                              setCategories((prev) => [...prev, cat])
                            } else {
                              setCategories((prev) =>
                                prev.filter((c) => c !== cat)
                              )
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
                            <p className="text-sm text-muted-foreground">
                              Set the price for your event.
                            </p>
                          </div>
                          <div className="grid grid-cols-2 gap-2">
                            <Input
                              type="number"
                              placeholder="0"
                              value={amount}
                              onChange={(e) =>
                                setAmount(
                                  Number.parseFloat(e.target.value) || 0
                                )
                              }
                            />
                            <Select
                              value={currency}
                              onValueChange={setCurrency}
                            >
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
                    <span>{isUnlimited ? "Unlimited" : capacity ?? 0}</span>
                    <Popover>
                      <PopoverTrigger asChild>
                        <Button variant="ghost" size="icon">
                          <Pencil className="h-4 w-4" />
                        </Button>
                      </PopoverTrigger>
                      <PopoverContent className="w-80">
                        <div className="grid gap-4">
                          <div className="space-y-2">
                            <h4 className="font-medium leading-none">
                              Capacity
                            </h4>
                            <p className="text-sm text-muted-foreground">
                              Set the maximum number of attendees.
                            </p>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Switch
                              id="unlimited-capacity"
                              checked={isUnlimited}
                              onCheckedChange={setIsUnlimited}
                            />
                            <Label htmlFor="unlimited-capacity">
                              Unlimited
                            </Label>
                          </div>
                          {!isUnlimited && (
                            <Input
                              type="number"
                              placeholder="Number of spots"
                              value={capacity ?? ""}
                              onChange={(e) =>
                                setCapacity(
                                  Number.parseInt(e.target.value, 10) || 0
                                )
                              }
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
            <Button
              className="w-full"
              type="submit"
              disabled={submitting || isUploading}
            >
              {submitting ? "Processing..." : `Create Event ($2 SGD Fee)`}
            </Button>
            <p className="text-sm text-muted-foreground text-center mt-2">
              A $2 SGD fee applies to all event listings. You&apos;ll be
              directed to payment after clicking the button.
            </p>
          </div>
        </div>
      </form>
    </div>
  )
}
