"use client";

import { EventDetails } from "@/types/event";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Calendar, Clock, MapPin, Users, Edit, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import Image from "next/image";

interface EventCardProps {
  event: EventDetails
  onEdit?: (eventId: string) => void
  onDelete?: (eventId: string) => void
}

export function HostingEventCard({ event, onEdit, onDelete }: EventCardProps) {
  const handleEdit = () => {
    if (onEdit) onEdit(event.id);
  };

  const handleDelete = () => {
    if (onDelete) onDelete(event.id);
  };

  return (
    <Card className="p-5 flex flex-col h-full overflow-hidden">
      {/* Event Image (if available) */}
      {event.imageUrl && (
        <div className="relative h-40 -mx-5 -mt-5 mb-4">
          <Image
            src={event.imageUrl}
            alt={event.title}
            fill
            className="object-cover"
          />
        </div>
      )}

      <div className="flex flex-col flex-grow">
        {/* Categories */}
        <div className="flex flex-wrap gap-2 mb-2">
          {event.categories.map((category, index) => (
            <Badge key={index} variant="secondary">
              {category as string}
            </Badge>
          ))}
        </div>

        {/* Title */}
        <h3 className="text-xl font-bold line-clamp-2 mb-3">{event.title}</h3>

        {/* Event Details */}
        <div className="space-y-2 text-sm text-muted-foreground mb-4 flex-grow">
          <div className="flex items-center">
            <Calendar className="w-4 h-4 mr-2 flex-shrink-0" />
            <span>{new Date(event.startDateTime).toLocaleDateString()}</span>
          </div>

          <div className="flex items-center">
            <Clock className="w-4 h-4 mr-2 flex-shrink-0" />
            <span>
              {new Date(event.startDateTime).toLocaleTimeString([], {
                hour: "2-digit",
                minute: "2-digit",
              })}
            </span>
          </div>

          {event.venue && (
            <div className="flex items-center">
              <MapPin className="w-4 h-4 mr-2 flex-shrink-0" />
              <span className="truncate">{event.venue.address}</span>
            </div>
          )}

          <div className="flex items-center">
            <Users className="w-4 h-4 mr-2 flex-shrink-0" />
            <span>
              Capacity: {event.capacity == 0 ? "No Capacity" : event.capacity}
            </span>
          </div>
        </div>
      </div>

      {/* Footer with Price and Actions */}
      <div className="flex justify-between items-center mt-4 pt-4 border-t">
        <div className="font-medium">
          {event.price > 0 ? `$${event.price.toFixed(2)} SGD` : "Free"}
        </div>

        <div className="flex items-center gap-2">
          {(onEdit || onDelete) && (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon">
                  <span className="sr-only">Open menu</span>
                  <svg
                    width="15"
                    height="15"
                    viewBox="0 0 15 15"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      d="M3.625 7.5C3.625 8.12132 3.12132 8.625 2.5 8.625C1.87868 8.625 1.375 8.12132 1.375 7.5C1.375 6.87868 1.87868 6.375 2.5 6.375C3.12132 6.375 3.625 6.87868 3.625 7.5ZM8.625 7.5C8.625 8.12132 8.12132 8.625 7.5 8.625C6.87868 8.625 6.375 8.12132 6.375 7.5C6.375 6.87868 6.87868 6.375 7.5 6.375C8.12132 6.375 8.625 6.87868 8.625 7.5ZM12.5 8.625C13.1213 8.625 13.625 8.12132 13.625 7.5C13.625 6.87868 13.1213 6.375 12.5 6.375C11.8787 6.375 11.375 6.87868 11.375 7.5C11.375 8.12132 11.8787 8.625 12.5 8.625Z"
                      fill="currentColor"
                      fillRule="evenodd"
                      clipRule="evenodd"
                    ></path>
                  </svg>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                {onEdit && (
                  <DropdownMenuItem onClick={handleEdit}>
                    <Edit className="w-4 h-4 mr-2" />
                    Edit Event
                  </DropdownMenuItem>
                )}
                {onDelete && (
                  <DropdownMenuItem
                    className="text-destructive"
                    onClick={handleDelete}
                  >
                    <Trash2 className="w-4 h-4 mr-2" />
                    Delete Event
                  </DropdownMenuItem>
                )}
              </DropdownMenuContent>
            </DropdownMenu>
          )}

          <Button asChild variant="outline" size="sm">
            <Link href={`/events/${event.id}`}>View Details</Link>
          </Button>
        </div>
      </div>
    </Card>
  );
}
