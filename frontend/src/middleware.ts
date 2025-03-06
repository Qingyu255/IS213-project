import { type NextRequest, NextResponse } from "next/server";
import { Route } from "./constants/routes";
import { PROTECTED_ROUTES } from "./constants/protected-routes";
import { fetchAuthSession } from "aws-amplify/auth";

export async function middleware(request: NextRequest) {
  const response = NextResponse.next();
  
  // const user = await authenticatedUser({ request, response });
  const session = await fetchAuthSession();
  const token = session.tokens?.accessToken;
  console.log(`User authenticated Token: ${token}`)
  
  const currentRoute = request.nextUrl.pathname;
  const isProtectedRoute = PROTECTED_ROUTES.some(route =>
    currentRoute.startsWith(route)
  );

  if (isProtectedRoute && !token) {
    console.log(`Unauthenticated user trying to access protected route ${currentRoute}'. Redirecting to login page.`)
    return NextResponse.redirect(new URL(Route.Login, request.nextUrl));
  }
  
  return response;
}

export const config = {
  /*
   * Match all request paths except for the ones starting with
   */
  matcher: ["/((?!api|_next/static|_next/image|.*\\.png$).*)"],
};