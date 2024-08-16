"use client";

import { useEffect, useState } from "react";
import { toast } from "react-toastify";

type ProofRequest = {
  name: string;
  description: string;
  ai_model_name: string;
};

export default function Me() {
  const [proofRequests, setProofRequests] = useState<ProofRequest[]>([]);

  useEffect(() => {
    const fetchProofRequests = async () => {
      try {
        const response = await fetch(`/api/proof_requests`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: "include",
        })
        if (response.ok) {
          const data = await response.json();
          setProofRequests(data);
        } else {
          toast.error("Failed to fetch proof requests");
        }
      } catch (error) {
        toast.error("Failed to fetch proof requests");
      }
    }

    fetchProofRequests();
  }, []);

  return (
    <div className="bg-gray-900 py-12 sm:py-24 h-screen">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="mx-auto max-w-4xl text-center">
          <h2 className="mt-2 text-4xl font-bold tracking-tight text-white sm:text-5xl">
            All my proof requests
          </h2>
        </div>
        <p className="mx-auto mt-2 max-w-2xl text-center text-lg leading-8 text-gray-300">
          Visualize here all your proof requests and their status.
        </p>

        <div className="flex justify-center mt-8">
          <div className="grid grid-cols-1 gap-8">
            {
              proofRequests && proofRequests.length > 0 && proofRequests.map((proofRequest, index) => (
                <div
                  key={index}
                  className="flex flex-col min-w-80 max-w-sm p-4 bg-white border border-gray-200 rounded-lg shadow hover:bg-gray-100 dark:bg-gray-800 dark:border-gray-700 dark:hover:bg-gray-700"
                >
                  <h4 className="text-left mb-2 text-lg font-bold tracking-tight text-gray-900 dark:text-white">
                    {proofRequest.name}
                  </h4>
                  <p className="text-left text-sm text-gray-700 dark:text-gray-400">
                    {proofRequest.description}
                  </p>
                  <p className="text-left text-sm text-gray-700 dark:text-gray-400">
                    {`Model name: ${proofRequest.ai_model_name}`}
                  </p>

                </div>
              ))
            }
          </div>
        </div>
      </div>
    </div>
  ); ``
}
