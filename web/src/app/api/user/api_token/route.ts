import { getLogged } from "@/utils/login";

const backendUrl = process.env.BACKEND_URL || "http://localhost:8000";
const backendAuthToken = process.env.BACKEND_AUTH_TOKEN || "";

export async function POST(req: Request) {
  const session = await getLogged();

  const ownerWallet = (session as any).ctx.wallet

  const response = await fetch(`${backendUrl}/user/api_token`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Auth-Token": backendAuthToken,
    },
    body: JSON.stringify({
      address: ownerWallet
    })
  })

  if (!response.ok) {
    console.log("Failed to fetch user data");
    return Response.json({
      error: "Failed to fetch user data",
    }, {
      status: 500
    });
  }

  const data = await response.json();
  console.log({ data })

  return Response.json(data, { status: 200 });
}
