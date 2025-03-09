"use client";

import * as React from "react";
import { Check, CircleAlert } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";

interface ConfirmationPopoverProps {
  message: string;
  onConfirm: () => void;
  children: React.ReactNode;
}

export function ConfirmationPopover({
  message,
  onConfirm,
  children,
}: ConfirmationPopoverProps) {
  const [open, setOpen] = React.useState(false);

  const handleConfirm = () => {
    onConfirm();
    setOpen(false);
  };

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>{children}</PopoverTrigger>
      <PopoverContent className="w-80">
        <div className="grid gap-4">
          <CircleAlert className="mx-auto"/>
          <div className="space-y-2">
            <p className="text-center text-base">{message}</p>
          </div>
          <div className="flex justify-center">
            <Button onClick={handleConfirm} className="w-24 font-bold">
              <Check className="mr-2 h-5 w-5 text-bold" /> Yes
            </Button>
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
}
