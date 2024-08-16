import { getLogged } from "@/utils/login";

const backendUrl = process.env.BACKEND_URL || "http://localhost:8000";
const backendAuthToken = process.env.BACKEND_AUTH_TOKEN || "";

export async function GET(req: Request) {
  const session = await getLogged();

  const ownerWallet = (session as any).ctx.wallet

  const response = await fetch(`${backendUrl}/proof_requests/${ownerWallet}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      "Auth-Token": backendAuthToken,
    },
  })

  if (!response.ok) {
    return Response.json({
      error: "Failed to create proof request",
    }, {
      status: 500
    });
  }

  const proofRequests = await response.json();

  return Response.json(proofRequests, { status: 200 });
}
