import React from "react";
import { Button } from "../ui/button";
import { MapPinned, Settings } from "lucide-react";

export default function Header() {
  return (
    <header className='fixed top-0 bg-stone-50 h-12 w-full flex flex-row items-center justify-between shadow-md'>
      <div className='flex flex-row items-center'>
        <Button variant='ghost' size='icon' className='size-10'>
          <MapPinned className='text-stone-600' />
        </Button>
        <h1 className='text-stone-600 ml-2 font-bold'>Störtebeker</h1>
      </div>
      <Button variant='ghost' size='icon' className='size-10'>
        <Settings className='text-stone-600' />
      </Button>
    </header>
  );
}
