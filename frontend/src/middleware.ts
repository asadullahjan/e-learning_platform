// frontend/middleware.ts
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  // Your middleware logic here
  console.log("Middleware running for:", request.url);

  // Check for authentication cookies
  const sessionCookie = request.cookies.get("sessionid");
  const csrfCookie = request.cookies.get("csrftoken");

  // Check if user is authenticated (has session cookie)
  const isAuthenticated = !!sessionCookie;

  console.log(
    "Auth check - Session:",
    !!sessionCookie,
    "CSRF:",
    !!csrfCookie,
    "Path:",
    request.nextUrl.pathname
  );

  // Allow access to auth pages, static assets, and API routes
  if (
    request.nextUrl.pathname.includes("/auth") ||
    request.nextUrl.pathname.includes("/_next") ||
    request.nextUrl.pathname.includes("/api") ||
    request.nextUrl.pathname.includes("/favicon.ico")
  ) {
    console.log("Allowing access to:", request.nextUrl.pathname);
    return NextResponse.next();
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated && !request.nextUrl.pathname.includes("/auth")) {
    console.log("User not authenticated, redirecting to login from:", request.nextUrl.pathname);
    return NextResponse.redirect(new URL("/auth/login", request.url));
  }

  // Redirect root to home if authenticated
  if (request.nextUrl.pathname === "/") {
    console.log("Authenticated user at root, redirecting to home");
    return NextResponse.redirect(new URL("/home", request.url));
  }

  console.log("Allowing authenticated access to:", request.nextUrl.pathname);
  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    "/((?!api|_next/static|_next/image|favicon.ico).*)",
  ],
};
