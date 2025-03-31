"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Badge } from "@/components/ui/badge";
import { InterestCategory } from "@/enums/InterestCategory";
import { format } from "date-fns";
import { Calendar as CalendarIcon, X } from "lucide-react";
import { cn } from "@/lib/utils";
import { DateRange } from "react-day-picker";

export interface EventFilters {
  categories: InterestCategory[];
  priceRange: [number, number];
  dateRange: {
    from: Date | undefined;
    to: Date | undefined;
  };
  showUnlimitedCapacity: boolean;
}

interface EventFiltersProps {
  onFilterChange: (filters: EventFilters) => void;
}

export function EventFilters({ onFilterChange }: EventFiltersProps) {
  const [selectedCategories, setSelectedCategories] = useState<InterestCategory[]>([]);
  const [priceRange, setPriceRange] = useState<[number, number]>([0, 1000]);
  const [dateRange, setDateRange] = useState<DateRange | undefined>();
  const [showUnlimitedCapacity, setShowUnlimitedCapacity] = useState(true);

  useEffect(() => {
    onFilterChange({
      categories: selectedCategories,
      priceRange,
      dateRange: {
        from: dateRange?.from,
        to: dateRange?.to,
      },
      showUnlimitedCapacity,
    });
  }, [selectedCategories, priceRange, dateRange, showUnlimitedCapacity, onFilterChange]);

  const handleCategoryToggle = (category: InterestCategory) => {
    setSelectedCategories(prev =>
      prev.includes(category)
        ? prev.filter(c => c !== category)
        : [...prev, category]
    );
  };

  const handlePriceRangeChange = (value: number[]) => {
    setPriceRange([value[0], value[1]]);
  };

  const handleDateRangeChange = (range: DateRange | undefined) => {
    setDateRange(range);
  };

  const handleCapacityToggle = (checked: boolean) => {
    setShowUnlimitedCapacity(checked);
  };

  const clearFilters = () => {
    setSelectedCategories([]);
    setPriceRange([0, 1000]);
    setDateRange(undefined);
    setShowUnlimitedCapacity(true);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Filters</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Categories */}
        <div className="space-y-2">
          <Label>Categories</Label>
          <div className="flex flex-wrap gap-2">
            {Object.values(InterestCategory).map((category) => (
              <Badge
                key={category}
                variant={selectedCategories.includes(category) ? "default" : "outline"}
                className="cursor-pointer"
                onClick={() => handleCategoryToggle(category)}
              >
                {category.charAt(0).toUpperCase() + category.slice(1)}
              </Badge>
            ))}
          </div>
        </div>

        {/* Price Range */}
        <div className="space-y-2">
          <Label>Price Range (SGD)</Label>
          <Slider
            value={priceRange}
            onValueChange={handlePriceRangeChange}
            min={0}
            max={1000}
            step={10}
            className="w-full"
          />
          <div className="flex justify-between text-sm text-muted-foreground">
            <span>SGD {priceRange[0]}</span>
            <span>SGD {priceRange[1]}</span>
          </div>
        </div>

        {/* Date Range */}
        <div className="space-y-2">
          <Label>Date Range</Label>
          <Popover>
            <PopoverTrigger asChild>
              <Button
                variant="outline"
                className={cn(
                  "w-full justify-start text-left font-normal",
                  !dateRange && "text-muted-foreground"
                )}
              >
                <CalendarIcon className="mr-2 h-4 w-4" />
                {dateRange?.from ? (
                  dateRange.to ? (
                    <>
                      {format(dateRange.from, "LLL dd, y")} -{" "}
                      {format(dateRange.to, "LLL dd, y")}
                    </>
                  ) : (
                    format(dateRange.from, "LLL dd, y")
                  )
                ) : (
                  <span>Pick a date range</span>
                )}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0" align="start">
              <Calendar
                initialFocus
                mode="range"
                defaultMonth={dateRange?.from}
                selected={dateRange}
                onSelect={handleDateRangeChange}
                numberOfMonths={2}
              />
            </PopoverContent>
          </Popover>
        </div>

        {/* Capacity Filter */}
        <div className="flex items-center justify-between">
          <Label>Show Unlimited Capacity</Label>
          <Switch
            checked={showUnlimitedCapacity}
            onCheckedChange={handleCapacityToggle}
          />
        </div>

        {/* Clear Filters */}
        <Button
          variant="outline"
          className="w-full"
          onClick={clearFilters}
        >
          <X className="mr-2 h-4 w-4" />
          Clear Filters
        </Button>
      </CardContent>
    </Card>
  );
} 