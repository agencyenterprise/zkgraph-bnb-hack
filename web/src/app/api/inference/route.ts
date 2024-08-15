import { getLogged } from "@/utils/login";

export async function POST(req: Request) {
  const data = await req.json();
  const session = await getLogged();

  const backendUrl = process.env.BACKEND_URL || "http://localhost:8000";
  const backendAuthToken = process.env.BACKEND_AUTH_TOKEN || "";
  const response = await fetch(`${backendUrl}/proof_requests`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Auth-Token": backendAuthToken,
    },
    body: JSON.stringify({
      name: "pr3",
      description: "pr3",
      graph_url: "pr3",
      ai_model_name: "",
      ai_model_inputs: ""
    })
  })

  console.log({response})

  return Response.json({
    session,
    data,
  });
}
