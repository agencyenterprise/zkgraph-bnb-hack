"use client";

import { useEffect, useState } from "react";
import { defineChain } from "thirdweb";
import { ConnectButton } from "thirdweb/react";
import { createWallet } from "thirdweb/wallets";

import { useChain } from "@/providers/chain";

import * as ethers from "ethers";

export default function MetaMaskConnect() {
  const { client, escrowBalance } = useChain();
  const [ammount, setAmmount] = useState<string>();

  const wallets = [
    createWallet("io.metamask"),
    createWallet("com.coinbase.wallet"),
    createWallet("me.rainbow"),
  ];

  useEffect(() => {
    if (escrowBalance != undefined) {
      try {
        setAmmount(ethers.formatEther(escrowBalance));
      } catch (e) {
        console.log("Error formating contract credits", e);
      }
    }
  }, [escrowBalance]);

  return (
    <div className="flex items-center justify-center text-white gap-2">
      {ammount && (
        <span className="text-sm font-semibold leading-6 text-white mx-2">
          Credits: {ammount}{" "}
        </span>
      )}

      {client && (
        <ConnectButton
          autoConnect={true}
          client={client}
          chain={defineChain(97)}
          wallets={wallets}
          theme={"dark"}
          connectModal={{ size: "wide" }}
        />
      )}
    </div>
  );
}
