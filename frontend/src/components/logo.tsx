import { siteName } from "@/constants/common";
import Image from "next/image";
import React from "react";

export default function Logo() {
  return (
    <div className="flex items-center gap-2">
      <div className="w-10 h-10 rounded-full bg-gradient-to-r from-purple-500 to-blue-500 flex items-center justify-center">
        <Image
          src="/bookaroo-white-logo.png"
          alt="Bookaroo Logo"
          width={25}
          height={25}
        />
      </div>
      <span className="text-xl font-bold tracking-tight">{siteName}</span>
    </div>
  );
}
