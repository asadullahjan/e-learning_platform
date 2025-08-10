"use server";

import { cookies } from "next/headers";

export async function getServerUser() {
  const cookieStore = await cookies();
  const sessionId = cookieStore.get("sessionid");

  if (!sessionId) {
    return null;
  }

  try {
    const response = await fetch(`${process.env.NEXT_PUBLIC_URL}/api/auth/profile/`, {
      headers: {
        Cookie: `sessionid=${sessionId.value}`,
      },
      credentials: "include",
      cache: "no-store",
    });

    if (response.ok) {
      return await response.json();
    }
  } catch (error) {
    console.error("Error fetching user:", error);
  }

  return null;
}

export async function isAuthenticated() {
  const user = await getServerUser();
  return user !== null;
}
