import { getLogged } from "@/utils/login";
import { STATUS_CODES } from "http";

export async function POST(req: Request) {
  const data = await req.json();

  console.log("data", data);

  
  const backendUrl = process.env.BACKEND_URL || "http://localhost:8000";
  const backendAuthToken = process.env.BACKEND_AUTH_TOKEN || "";
  const response = await fetch(`${backendUrl}/proof_requests`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Auth-Token": backendAuthToken,
    },
    body: JSON.stringify({
      name: data.name,
      description: data.description,
      graph_url: "",
      ai_model_name: "Iris",
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
