import { Label } from "@/components/ui/label";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import React from "react";

export default function Prices({
  value,
  setValue,
}: {
  value: string;
  setValue: (value: string) => void;
}) {
  return (
    <div>
      <Label>Money</Label>
      <ToggleGroup
        type='single'
        variant='outline'
        className='flex flex-wrap justify-start'
        value={value}
        onValueChange={(value) => setValue(value)}
      >
        <ToggleGroupItem value='1'>€</ToggleGroupItem>
        <ToggleGroupItem value='2'>€€</ToggleGroupItem>
        <ToggleGroupItem value='3'>€€€</ToggleGroupItem>
      </ToggleGroup>
    </div>
  );
}
