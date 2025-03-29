"use client";

import * as React from "react";
import { TimeIcon } from "lucide-react";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

interface TimePickerProps {
  setDate: (date: Date) => void
  date: Date
}

export function TimePickerDemo({ setDate, date }: TimePickerProps) {
  const minuteRef = React.useRef<HTMLInputElement>(null);
  const hourRef = React.useRef<HTMLInputElement>(null);
  const [hour, setHour] = React.useState<number>(date ? date.getHours() : 0);
  const [minute, setMinute] = React.useState<number>(date ? date.getMinutes() : 0);
  const [isPM, setIsPM] = React.useState<boolean>(date ? date.getHours() >= 12 : false);

  // Update the date when the hour or minute changes
  React.useEffect(() => {
    const newDate = new Date(date);
    newDate.setHours(isPM ? (hour === 12 ? 12 : hour + 12) : (hour === 12 ? 0 : hour));
    newDate.setMinutes(minute);
    setDate(newDate);
  }, [hour, minute, isPM, date, setDate]);

  return (
    <div className="flex items-end gap-2 p-4">
      <div className="grid gap-1 text-center">
        <Label htmlFor="hours" className="text-xs">
          Hours
        </Label>
        <Input
          ref={hourRef}
          id="hours"
          className="w-16 text-center"
          value={hour.toString().padStart(2, "0")}
          onChange={(e) => {
            const newHour = parseInt(e.target.value, 10);
            if (isNaN(newHour)) {
              setHour(0);
              return;
            }
            if (newHour > 12) {
              setHour(12);
              return;
            }
            if (newHour < 0) {
              setHour(0);
              return;
            }
            setHour(newHour);
          }}
          onKeyDown={(e) => {
            if (e.key === "ArrowUp") {
              e.preventDefault();
              setHour((prev) => (prev === 12 ? 1 : prev + 1));
            } else if (e.key === "ArrowDown") {
              e.preventDefault();
              setHour((prev) => (prev === 1 ? 12 : prev - 1));
            } else if (e.key === "ArrowRight" || e.key === "ArrowLeft") {
              e.preventDefault();
              minuteRef.current?.focus();
            }
          }}
        />
      </div>
      <div className="flex h-16 items-center">:</div>
      <div className="grid gap-1 text-center">
        <Label htmlFor="minutes" className="text-xs">
          Minutes
        </Label>
        <Input
          ref={minuteRef}
          id="minutes"
          className="w-16 text-center"
          value={minute.toString().padStart(2, "0")}
          onChange={(e) => {
            const newMinute = parseInt(e.target.value, 10);
            if (isNaN(newMinute)) {
              setMinute(0);
              return;
            }
            if (newMinute > 59) {
              setMinute(59);
              return;
            }
            if (newMinute < 0) {
              setMinute(0);
              return;
            }
            setMinute(newMinute);
          }}
          onKeyDown={(e) => {
            if (e.key === "ArrowUp") {
              e.preventDefault();
              setMinute((prev) => (prev === 59 ? 0 : prev + 1));
            } else if (e.key === "ArrowDown") {
              e.preventDefault();
              setMinute((prev) => (prev === 0 ? 59 : prev - 1));
            } else if (e.key === "ArrowRight" || e.key === "ArrowLeft") {
              e.preventDefault();
              hourRef.current?.focus();
            }
          }}
        />
      </div>
      <div className="flex h-16 items-center">
        <button
          type="button"
          className={cn(
            "rounded-md px-3 py-2 text-xs font-medium",
            isPM
              ? "bg-primary text-primary-foreground"
              : "bg-muted text-muted-foreground hover:bg-primary/90 hover:text-primary-foreground"
          )}
          onClick={() => setIsPM(true)}
        >
          PM
        </button>
      </div>
      <div className="flex h-16 items-center">
        <button
          type="button"
          className={cn(
            "rounded-md px-3 py-2 text-xs font-medium",
            !isPM
              ? "bg-primary text-primary-foreground"
              : "bg-muted text-muted-foreground hover:bg-primary/90 hover:text-primary-foreground"
          )}
          onClick={() => setIsPM(false)}
        >
          AM
        </button>
      </div>
    </div>
  );
} 