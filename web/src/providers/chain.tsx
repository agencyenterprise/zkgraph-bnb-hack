"use client";

import React, {
  createContext,
  useContext,
  useState,
  useMemo,
  useEffect,
  useCallback,
} from "react";
import {
  createThirdwebClient,
  defineChain,
  getContract,
  readContract,
} from "thirdweb";
import { useActiveAccount } from "thirdweb/react";
import * as ethers from "ethers";
import { client } from "@/utils/auth";

// Create the context
const ChainContext = createContext({
  client: {} as ReturnType<typeof createThirdwebClient>,
  escrowContract: {} as ReturnType<typeof getContract> | undefined,
  escrowBalance: {} as bigint | undefined,
  fetchEscrowBalance: () => {},
});

// Provider component
export function ChainProvider({ children }: { children: React.ReactNode }) {
  const [escrowContract, setEscrowContract] =
    useState<ReturnType<typeof getContract>>();
  const [escrowBalance, setEscrowBalance] = useState<bigint>();

  const activeAccount = useActiveAccount();

  const fetchEscrowBalance = useCallback(() => {
    if (activeAccount && escrowContract) {
      const fetchBalance = async () => {
        const balance = await readContract({
          contract: escrowContract,
          method: "function balanceOf(address) view returns (uint256)",
          params: [activeAccount.address],
        });

        setEscrowBalance(ethers.toBigInt(balance));
      };

      fetchBalance();
    }
  }, [activeAccount, escrowContract]);

  useEffect(() => {
    if (client) {
      const newEscrowContract = getContract({
        client,
        chain: defineChain(97),
        address: process.env.NEXT_PUBLIC_ESCROW_ADDRESS || "",
      });
      setEscrowContract(newEscrowContract);
    }
  }, []);

  useEffect(() => {
    fetchEscrowBalance();
  }, [activeAccount, escrowContract, fetchEscrowBalance]);

  // Memoize the context value to optimize performance
  const value = useMemo(
    () => ({
      client,
      escrowContract,
      escrowBalance,
      fetchEscrowBalance,
    }),
    [escrowContract, escrowBalance, fetchEscrowBalance],
  );

  return (
    <ChainContext.Provider value={value}>{children}</ChainContext.Provider>
  );
}

// Custom hook for accessing the context
export function useChain() {
  const context = useContext(ChainContext);
  if (!context) {
    throw new Error("useChain must be used within a ChainProvider");
  }
  return context;
}
