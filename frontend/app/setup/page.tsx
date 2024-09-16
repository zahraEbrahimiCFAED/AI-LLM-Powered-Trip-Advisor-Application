"use client";

import React, { useEffect } from "react";
import { DatePickerWithRange } from "./_components/date-time-picker";
import PointOfInternets from "./_components/points-of-internets";
import { addDays } from "date-fns";
import { DateRange } from "react-day-picker";
import Duration from "./_components/duration";
import Prices from "./_components/prices";
import { Button } from "@/components/ui/button";
import { Sparkles } from "lucide-react";
import { useRouter } from "next/navigation";

export default function Setup() {
  const router = useRouter();
  const today = Date.now();
  const [date, setDate] = React.useState<DateRange | undefined>({
    from: new Date(today),
    to: addDays(new Date(today), 7),
  });
  const [pointsOfInterest, setPointsOfInterest] = React.useState<string[]>([]);
  const [duration, setDuration] = React.useState<string>("1-3");
  const [price, setPrice] = React.useState<string>("");
  const [location, setLocation] = React.useState<GeolocationPosition>();

  useEffect(() => {
    function getLocation() {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition((l) => setLocation(l));
      }
    }

    getLocation();

    return () => {};
  }, []);

  const sendMsg = async () => {
    const url = process.env.NEXT_PUBLIC_BACKEND_URL;
    // verify backend URL
    if (!url) {
      console.error("Backend URL not set");
      return;
    }
    try {
      // POST to backend
      const res = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          date,
          pointsOfInterest,
          duration,
          price,
          location,
        }),
      });
      const data = await res.json();
      if (data.error) {
        console.error(data.error);
        return;
      }
      localStorage.setItem(
        "setup",
        JSON.stringify({
          date,
          pointsOfInterest,
          duration,
          price,
          location,
        })
      );
      router.push("/");
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div className='h-full w-full flex flex-col p-4'>
      <h1 className='text-5xl '>Setup</h1>
      <p className='text-base'>Select the activities you are interested in.</p>
      <div className='my-4' />
      <div className='flex flex-col gap-8 w-full'>
        <PointOfInternets
          value={pointsOfInterest}
          setValue={setPointsOfInterest}
        />
        <DatePickerWithRange date={date} setDate={setDate} />
        <Duration value={duration} setValue={setDuration} />
        <Prices value={price} setValue={setPrice} />
      </div>
      <div className='my-2' />
      <Button className='self-end gap-2' variant='default' onClick={sendMsg}>
        Start Exploring
        <Sparkles className='stroke-1' />
      </Button>
    </div>
  );
}
