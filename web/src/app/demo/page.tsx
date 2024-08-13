"use client";

import { CheckIcon } from "@heroicons/react/20/solid";
import Button from "@/components/button";
import { useChain } from "@/providers/chain";

import { useActiveAccount } from "thirdweb/react";
import { useState } from "react";
import { toast } from "react-toastify";

export default function BuyPage() {
  const [customPrice, setCustomPrice] = useState<string>("100");
  const { client, escrowContract, fetchEscrowBalance } = useChain();
  const activeAccount = useActiveAccount();

  const handleInference = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!client || !escrowContract || !activeAccount) {
      return;
    }

    try {
      const response = await fetch("/api/inference", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ customPrice }),
      });

      if (response.ok) {
        // Handle successful response
        const data = await response.json();
        console.log("data", data);
      } else {
        const message = "Error generating inference";
        console.log(message);
        toast.error(message + e);
      }
    } catch (error) {
      const message = "Error generating inference";
      console.log(message);
      toast.error(message + error);
    }
  };

  return (
    <div className="bg-gray-900 py-16 sm:py-32 min-h-screen">
      <form onSubmit={handleInference}>
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <Button
            id={`button-submit`}
            type="submit"
            label={"Generate Inference"}
          />
        </div>
      </form>
    </div>
  );
}
