// frontend/middleware.ts
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  // Your middleware logic here
  console.log("Middleware running for:", request.url);
  const token = request.cookies.get("sessionid");
  if (!token && !request.nextUrl.pathname.includes("/auth")) {
    return NextResponse.redirect(new URL("/auth/login", request.url));
  } else if (request.nextUrl.pathname === "/") {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }
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
