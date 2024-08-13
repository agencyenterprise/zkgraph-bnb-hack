import { getLogged } from "@/lib/login";

export async function POST(req: Request) {
  const data = await req.json();

  console.log("payload", data);

  const session = await getLogged();

  console.log("session", session);

  return Response.json({
    session,
    data,
  });
}
