import { getLogged } from "@/utils/login";

export async function POST(req: Request) {
  const session = await getLogged();
  const data = await req.json();

  const ownerWallet = (session as any).ctx.wallet

  const backendUrl = process.env.BACKEND_URL || "http://localhost:8000";
  const backendAuthToken = process.env.BACKEND_AUTH_TOKEN || "";

  const response = await fetch(`${backendUrl}/proof_requests`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Auth-Token": backendAuthToken,
    },
    body: JSON.stringify({
      owner_wallet: ownerWallet,
      name: data.name,
      description: data.description,
      ai_model_name: "iris_model",
      ai_model_inputs: data.jsonInput,
    })
  })

  if (!response.ok) {
    return Response.json({
      error: "Failed to create proof request",
    }, {
      status: 500
    });
  }

  const proofRequest = await response.json();

  return Response.json(proofRequest, { status: 200 });
}
