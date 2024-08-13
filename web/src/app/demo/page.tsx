"use client";

import { CheckIcon } from "@heroicons/react/20/solid";
import Button from "@/components/button";
import { useChain } from "@/providers/chain";

import { useActiveAccount } from "thirdweb/react";
import { useState } from "react";

export default function BuyPage() {
  const [customPrice, setCustomPrice] = useState<string>("100");
  const { client, escrowContract, fetchEscrowBalance } = useChain();
  const activeAccount = useActiveAccount();

  const handleInference = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!client || !escrowContract || !activeAccount) {
      return;
    }
    //TODO handle buy credits
  };

  return (
    <div className="bg-gray-900 py-16 sm:py-32 min-h-screen">
      <form onSubmit={handleInference}>
        <div className="mx-auto max-w-7xl px-6 lg:px-8"></div>
      </form>
    </div>
  );
}
