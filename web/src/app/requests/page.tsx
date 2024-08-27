"use client";

import Button from "@/components/button";
import Loading from "@/components/loading";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { toast } from "react-toastify";
import Link from "next/link";

type ProofRequest = {
  name: string;
  description: string;
  ai_model_name: string;
  status: string;
  worker_wallet: string;
};

export default function Me() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [proofRequests, setProofRequests] = useState<ProofRequest[]>([]);

  useEffect(() => {
    const fetchProofRequests = async () => {
      setLoading(true);
      try {
        const response = await fetch(`/api/proof_requests`, {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
        });
        if (response.ok) {
          const data = await response.json();
          setProofRequests(data);
        } else {
          toast.error("Failed to fetch proof requests");
        }
      } catch (error) {
        toast.error("Failed to fetch proof requests");
      } finally {
        setLoading(false);
      }
    };

    fetchProofRequests();
  }, []);

  return (
    <div className="bg-tertiary-900 py-12 sm:py-24 min-h-screen">
      <div className="mx-auto w-full sm:max-w-2xl px-4 sm:px-8">
        <div className="mx-auto max-w-4xl text-center py-8">
          <h2 className="text-2xl font-bold tracking-tight text-secondary-100 sm:text-4xl">
            All my proof requests
          </h2>
        </div>
        <p className="mx-auto max-w-2xl text-center text-xl font-bold leading-8 text-primary-500 py-0 sm:py-4 mt-2">
          Visualize here all your proof requests and their status.
        </p>

        <div className="flex justify-center mt-8">
          {loading ? (
            <div className="mb-6 flex justify-center">
              <Loading size="500px" />
            </div>
          ) : proofRequests?.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-8">
              {proofRequests.map((proofRequest, index) => (
                <div
                  key={index}
                  className="flex flex-col p-4 bg-tertiary-800 border border-secondary-500 rounded-lg shadow hover:bg-tertiary-700 w-full"
                >
                  <h4 className="text-left mb-2 text-lg font-bold tracking-tight text-secondary-100">
                    {proofRequest.name}
                  </h4>
                  <p className="text-left text-sm text-secondary-200">
                    {proofRequest.description}
                  </p>
                  <p className="text-left text-sm text-secondary-200">
                    {`Model name: ${proofRequest.ai_model_name}`}
                  </p>
                  <p className="text-left text-sm text-secondary-200">
                    {`Status: ${proofRequest.status}`}
                  </p>
                  {proofRequest.worker_wallet != "None" && <p className="text-left text-sm text-secondary-200">
                    Paid to worker:{' '}
                    <Link
                      href={`https://testnet.bscscan.com/address/${proofRequest.worker_wallet}`}
                      target="_blank"
                      className="underline text-primary-500 hover:text-primary-400"
                    >
                      {proofRequest.worker_wallet.slice(0, 6)}...{proofRequest.worker_wallet.slice(-4)}
                    </Link>
                  </p>}
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center text-secondary-200">
              No proof requests found
              <Button
                id={`button-started`}
                type="button"
                label="Get started"
                className="ml-8"
                onClick={() => {
                  router.push("/requestProof");
                }}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
