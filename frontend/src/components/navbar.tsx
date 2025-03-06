"use client"
import { Route } from "@/constants/routes";
import { Menu } from "lucide-react";
import Link from "next/link";
import React from "react";
import { ModeToggle } from "./mode-toggle";
import { Button } from "./ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from "./ui/dropdown-menu";
import Logo from "./logo";
import useAuthUser from "@/app/hooks/use-auth-user";
import { handleSignOut } from "@/lib/cognitoActions";


export default function Navbar() {
  const user = useAuthUser();
  // const isLoggedIn = false;
  return (
    <div className="relative z-10 border-b bg-transparent">
      <div className="container mx-auto px-4 py-4 flex items-center justify-between">
        {/* Logo Section */}
        <Link href={"/"}>
          <Logo />
        </Link>

        {/* Desktop Navigation & Action Buttons */}
        <div className="hidden md:flex items-center gap-3">
          <nav className="flex items-center space-x-6">
            <Link
              href={Route.BrowseEvents}
              className="text-sm font-medium transition-colors duration-200"
            >
              Browse Events
            </Link>
            <Link
              href={Route.CreateEvent}
              className="text-sm font-medium transition-colors duration-200"
            >
              Create Event
            </Link>
            <Link
              href="#"
              className="text-sm font-medium transition-colors duration-200"
            >
              Pricing
            </Link>
          </nav>
          <div className="flex items-center gap-4 ml-0">
            {user && user.isLoggedIn ? (
              <Button onClick={handleSignOut} className="bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600 border-0 transition-colors duration-200">
                Logout
              </Button>
            ) : (
              <Link href={Route.Login}>
                <Button className="bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600 border-0 transition-colors duration-200">
                  Sign In
                </Button>
              </Link>
            )}
            
            <ModeToggle />
          </div>
        </div>

        {/* Mobile Navigation: Keep Sign In Visible and Use Dropdown for Others */}
        <div className="flex md:hidden items-center gap-4">
          {user && user.isLoggedIn ? (
              <Button onClick={handleSignOut} className="bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600 border-0 transition-colors duration-200">
                Logout
              </Button>
            ) : (
              <Link href={Route.Login}>
                <Button className="bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600 border-0 transition-colors duration-200">
                  Sign In
                </Button>
              </Link>
            )}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button aria-label="Toggle Menu" className="p-2">
                <Menu className="w-6 h-6" />
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              <DropdownMenuItem asChild>
                <Link href={Route.BrowseEvents}>Browse Events</Link>
              </DropdownMenuItem>
              <DropdownMenuItem asChild>
                <Link href={Route.CreateEvent}>Create Event</Link>
              </DropdownMenuItem>
              <DropdownMenuItem asChild>
                <Link href="#">Pricing</Link>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem asChild>
                <Button className="w-full bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600 border-0 transition-colors duration-200">
                  Get Started
                </Button>
              </DropdownMenuItem>
              <DropdownMenuItem asChild>
                <div className="w-full flex justify-end mt-3">
                  <ModeToggle />
                </div>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </div>
  );
}
