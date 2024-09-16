import { Label } from "@/components/ui/label";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import React from "react";

export default function PointOfInternets({
  value,
  setValue,
}: {
  value: string[];
  setValue: (value: string[]) => void;
}) {
  return (
    <div>
      <Label>Points of Interest</Label>
      <ToggleGroup
        type='multiple'
        variant='outline'
        className='flex flex-wrap justify-start'
        value={value}
        onValueChange={(value) => setValue(value)}
      >
        <ToggleGroupItem value='museum'>Museum</ToggleGroupItem>
        <ToggleGroupItem value='historic'>Historic</ToggleGroupItem>
        <ToggleGroupItem value='nature'>Nature</ToggleGroupItem>
        <ToggleGroupItem value='shopping'>Shopping</ToggleGroupItem>
        <ToggleGroupItem value='dining'>Dining</ToggleGroupItem>
        <ToggleGroupItem value='entertainment'>Entertainment</ToggleGroupItem>
      </ToggleGroup>
    </div>
  );
}
