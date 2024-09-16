import React from "react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";

export default function Duration({
  value,
  setValue,
}: {
  value: string;
  setValue: (value: string) => void;
}) {
  return (
    <div>
      <Label>Duration</Label>
      <Select onValueChange={setValue} value={value}>
        <SelectTrigger className='w-full'>
          <SelectValue placeholder='Duration' />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value='1-3'>1-3 hours</SelectItem>
          <SelectItem value='4-6'>4-6 hours</SelectItem>
          <SelectItem value='7-10'>7-10 hours</SelectItem>
          <SelectItem value='10-16'>11-16 hours</SelectItem>
        </SelectContent>
      </Select>
    </div>
  );
}
