"use client"
import { useParams } from "next/navigation";
import ConfirmSignUpForm from "./components/confirm-signup-form";

export default function LoginPage() {
  const { userName } = useParams() as { userName: string }; // dynamic route param

  return <ConfirmSignUpForm userName = {userName} />;
}
