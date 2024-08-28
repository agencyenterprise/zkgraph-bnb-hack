"use client";

import Button from "@/components/button";
import Loading from "@/components/loading";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { toast } from "react-toastify";
import Link from "next/link";

type ProofRequest = {
  id: string;
  name: string;
  description: string;
  ai_model_name: string;
  status: string;
  worker_wallet: string;
  proof: string;
};

export default function Me() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [proofRequests, setProofRequests] = useState<ProofRequest[]>([]);
  const [selectedProofRequest, setSelectedProofRequest] =
    useState<ProofRequest>();
  const [showMore, setShowMore] = useState(false);

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

  useEffect(() => {
    setShowMore(false);
  }, [selectedProofRequest]);

  const NoProofRequests = () => {
    return (
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
    );
  };

  const ProofRequestsList = () => {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-8">
        {proofRequests.map((proofRequest, index) => (
          <div
            key={index}
            className="flex flex-col p-4 bg-tertiary-800 border border-secondary-500 rounded-lg shadow hover:bg-tertiary-700 w-full cursor-pointer"
            onClick={() => setSelectedProofRequest(proofRequest)}
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
            {proofRequest.worker_wallet != "None" && (
              <p className="text-left text-sm text-secondary-200">
                Paid to worker:{" "}
                <Link
                  href={`https://testnet.bscscan.com/address/${proofRequest.worker_wallet}`}
                  target="_blank"
                  className="underline text-primary-500 hover:text-primary-400"
                >
                  {proofRequest.worker_wallet.slice(0, 6)}...
                  {proofRequest.worker_wallet.slice(-4)}
                </Link>
              </p>
            )}
          </div>
        ))}
      </div>
    );
  };

  const ProofRequestDetails = () => {
    if (!selectedProofRequest) {
      return null;
    }

    return (
      <div className="flex flex-col w-full">
        <div className="flex flex-col p-4 bg-tertiary-800 border border-secondary-500 rounded-lg shadow w-full">
          <h4 className="text-left mb-2 text-lg font-bold tracking-tight text-secondary-100">
            {selectedProofRequest.name}
          </h4>
          <p className="text-left text-sm text-secondary-200">
            {selectedProofRequest.description}
          </p>
          <p className="text-left text-sm text-secondary-200">
            {`Model name: ${selectedProofRequest.ai_model_name}`}
          </p>
          <p className="text-left text-sm text-secondary-200">
            {`Status: ${selectedProofRequest.status}`}
          </p>
          {selectedProofRequest.worker_wallet != "None" && (
            <p className="text-left text-sm text-secondary-200">
              Paid to worker:{" "}
              <Link
                href={`https://testnet.bscscan.com/address/${selectedProofRequest.worker_wallet}`}
                target="_blank"
                className="underline text-primary-500 hover:text-primary-400"
              >
                {selectedProofRequest.worker_wallet}
              </Link>
            </p>
          )}
          {selectedProofRequest.proof != "None" && (
            <p className="break-all text-left text-sm text-secondary-200">
              Proof:{" "}
              {showMore && (
                <>
                  <div>{selectedProofRequest.proof}</div>
                  <Button
                    id={`button-show-less`}
                    type="button"
                    label="Show less"
                    className="mt-2 px-2.5 py-1.5 font-normal outline-black"
                    onClick={() => setShowMore(false)}
                  />
                </>
              )}
              {!showMore && (
                <>
                  <div>{selectedProofRequest.proof.slice(0, 500)}...</div>
                  <Button
                    id={`button-show-more`}
                    type="button"
                    label="Show more"
                    className="mt-2 px-2.5 py-1.5 font-normal outline-black"
                    onClick={() => setShowMore(true)}
                  />
                </>
              )}
            </p>
          )}
        </div>

        <div className="flex justify-center mt-8">
          <Button
            id={`button-started`}
            type="button"
            label="Back"
            className="ml-8"
            onClick={() => setSelectedProofRequest(undefined)}
          />
        </div>
      </div>
    );
  };

  return (
    <div className="bg-tertiary-900 py-12 sm:py-24 min-h-screen">
      <div className="mx-auto w-full sm:max-w-2xl px-4 sm:px-8">
        <div className="mx-auto max-w-4xl text-center py-8">
          <h2 className="text-2xl font-bold tracking-tight text-secondary-100 sm:text-4xl">
            Proof Request History
          </h2>
        </div>
        <div className="flex justify-center mt-8">
          {loading && (
            <div className="mb-6 flex justify-center">
              <Loading size="500px" />
            </div>
          )}

          {!loading && (
            <>
              {selectedProofRequest && <ProofRequestDetails />}
              {!selectedProofRequest && proofRequests?.length > 0 && (
                <ProofRequestsList />
              )}
              {!selectedProofRequest && proofRequests?.length == 0 && (
                <NoProofRequests />
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
