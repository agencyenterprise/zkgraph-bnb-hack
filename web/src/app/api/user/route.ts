import { getLogged } from "@/utils/login";

const backendUrl = process.env.BACKEND_URL || "http://localhost:8000";
const backendAuthToken = process.env.BACKEND_AUTH_TOKEN || "";

export async function GET(req: Request) {
  const session = await getLogged();

  const ownerWallet = (session as any).ctx.wallet

  const response = await fetch(`${backendUrl}/user/${ownerWallet}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      "Auth-Token": backendAuthToken,
    },
  })

  if (!response.ok) {
    console.log("Failed to fetch user data", response);
    return Response.json({
      error: "Failed to fetch user data",
    }, {
      status: 500
    });
  }

  const user = await response.json();

  return Response.json(user, { status: 200 });
}
