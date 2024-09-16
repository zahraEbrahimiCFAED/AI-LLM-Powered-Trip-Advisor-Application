"use client";

import React, { useEffect } from "react";
import { Button } from "../ui/button";
import L from "leaflet";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import dynamic from "next/dynamic"; // Import dynamic from next/dynamic

// Dynamically import the MapContainer component with SSR disabled
const MapContainer = dynamic(
  () => import("react-leaflet").then((mod) => mod.MapContainer),
  { ssr: false }
);
const TileLayer = dynamic(
  () => import("react-leaflet").then((mod) => mod.TileLayer),
  { ssr: false }
);
const Marker = dynamic(
  () => import("react-leaflet").then((mod) => mod.Marker),
  { ssr: false }
);
const Popup = dynamic(() => import("react-leaflet").then((mod) => mod.Popup), {
  ssr: false,
});

import Link from "next/link";
import "leaflet/dist/leaflet.css";
import { LatLngExpression } from "leaflet";

export default function RiddleDialog({
  name,
  question,
  location_website,
  long_description,
  address,
  title,
  coordinates,
}: {
  name: string;
  question: string;
  location_website: string;
  long_description: string;
  address: string;
  title: string;
  coordinates: any;
}) {
  const [isOpen, setIsOpen] = React.useState(false);

  function transformCoordinates(coordinateString: string) {
    try {
      if (coordinateString === undefined)
        return { lat: 54.48544754922814, lng: 13.506159847849649 };
      // Remove the parentheses and split the string by comma
      const cleanedString = coordinateString?.replace(/[()]/g, "");
      const parts = cleanedString.split(",").map((part) => part.trim());

      // Convert the string parts to numbers
      const coordinatesArray = parts.map(Number);

      return coordinatesArray as LatLngExpression;
    } catch (error) {
      return { lat: 54.48544754922814, lng: 13.506159847849649 };
    }
  }
  const position: LatLngExpression = transformCoordinates(coordinates);
  useEffect(() => {
    // Dynamically import Leaflet to avoid SSR issues
    const L = require("leaflet");

    const DefaultIcon = L.icon({
      iconUrl:
        "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png",
      shadowUrl:
        "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
      iconSize: [25, 41], // Size of the icon
      iconAnchor: [12, 41], // Point of the icon which will correspond to marker's location
      popupAnchor: [1, -34], // Point from which the popup should open relative to the iconAnchor
      shadowSize: [41, 41], // Size of the shadow
    });

    // Apply this icon globally so you don't have to specify it each time
    L.Marker.prototype.options.icon = DefaultIcon;
  }, []); // Run once on mount

  return (
    <Dialog modal open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger className='self-start'>
        <Button className='self-start'>More Information</Button>
      </DialogTrigger>
      <DialogContent className='bg-white h-full overflow-auto'>
        <DialogHeader>
          <DialogTitle className='w-full flex'>{title}</DialogTitle>
        </DialogHeader>
        {/* description */}
        <p className='text-sm'>{long_description}</p>
        {/* link */}
        <Link href={location_website ?? "http://google.com"}>
          <p className='underline text-blue-500'>Visit their Website</p>
        </Link>

        {/* map */}
        {position && (
          <div className='w-full h-36'>
            <h1 className='text-5xl font-bold'>{name}</h1>
            <MapContainer className='w-full h-full' center={position} zoom={13}>
              <TileLayer url='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png' />
              <Marker position={position}>
                <Popup>{title}</Popup>
              </Marker>
            </MapContainer>
            <p className='text-sm italic text-stone-400'>{address}</p>
          </div>
        )}
        <DialogFooter>
          <Button className='mt-8' onClick={() => setIsOpen(false)}>
            Back to Chat
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
