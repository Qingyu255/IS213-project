import { redirect } from "next/navigation";
import {
  confirmSignUp,
  signIn,
  signOut,
  resendSignUpCode,
} from "aws-amplify/auth";
import { Route } from "@/constants/routes";

export async function handleSignIn(
  prevState: string | undefined,
  formData: FormData
) {
  let redirectLink = Route.BrowseEvents as string;
  try {
    const { nextStep } = await signIn({
      username: String(formData.get("email")),
      password: String(formData.get("password")),
    });
    if (nextStep.signInStep === "CONFIRM_SIGN_UP") {
      await resendSignUpCode({
        username: String(formData.get("email")),
      });
      redirectLink = Route.ConfirmSignUp;
    }
  } catch (error) {
    return getErrorMessage(error);
  }

  redirect(redirectLink);
}

export async function handleSignOut() {
  try {
    await signOut();
  } catch (error) {
    console.log(getErrorMessage(error));
  }
  console.debug("User logged out")
  redirect(Route.Login);
}

export function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }
  if (error && typeof error === "object" && "message" in error) {
    return String(error.message);
  }
  if (typeof error === "string") {
    return error;
  }
  return "An error occurred";
}
export { confirmSignUp };

