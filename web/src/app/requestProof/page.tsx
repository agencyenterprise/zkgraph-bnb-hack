"use client";

import Button from "@/components/button";
import { useChain } from "@/providers/chain";
import { useActiveAccount } from "thirdweb/react";
import { useEffect, useState } from "react";
import { toast } from "react-toastify";
import { isValidJson } from "@/utils/json";
import JsonInput from "@/components/json-input";
import { useRouter } from "next/navigation";
import { twMerge } from "tailwind-merge";
import Loading from "@/components/loading";
import * as ethers from "ethers";
import Link from "next/link";

type Data = {
  name?: string;
  description?: string;
  jsonInput?: string;
};

const modelOptions = [
  {
    name: "Iris model",
    modelId: "iris_model",
    description:
      "This model generates a prediction on whether you are a human being or a ladybird",
  },
  {
    name: "Incoming model",
    description: "Incoming model",
  },
];

export default function BuyPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<Data>({});
  const [currentStep, setCurrentStep] = useState<number>(1);
  const [selectedModelOption, setSelectedModelOption] = useState<
    number | undefined
  >();
  const { client, escrowBalance, escrowContract } = useChain();
  const activeAccount = useActiveAccount();
  const [amount, setAmount] = useState<string>();

  useEffect(() => {
    if (escrowBalance != undefined) {
      try {
        setAmount(ethers.formatEther(escrowBalance));
      } catch (e) {
        console.log("Error formating contract credits", e);
      }
    }
  }, [escrowBalance]);

  const handleInference = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!client || !escrowContract || !activeAccount) {
      toast.error("Make sure your wallet is connected");
      return;
    }
    setLoading(true);
    try {
      const response = await fetch("/api/inference", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        setLoading(false);
        router.push("/requests");
      } else {
        const message = "Error generating inference";
        console.log(message, e);
        toast.error(message);
      }
    } catch (error) {
      const message = "Error generating inference";
      console.log(message, e);
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-tertiary-900 py-20 sm:py-32 min-h-screen">
      <form onSubmit={handleInference}>
        <div className="mx-auto w-full sm:max-w-2xl">
          <h1 className="text-2xl sm:text-4xl font-bold tracking-tight text-secondary-100 pb-0 sm:pb-3 text-center mx-auto">
            Proof Request
          </h1>
          {loading ? (
            <div className="mb-6 flex justify-center">
              <Loading size="500px" />
            </div>
          ) : currentStep === 1 ? (
            <div className="py-8 px-4">
              {Number(amount) === 0 && <div className="bg-orange-100 border-l-4 border-orange-500 text-orange-700 p-4 mb-3" role="alert">
                <p>You must have some credits to request a proof</p>
                <p className="font-bold">
                  <Link href="/buy">
                    Click here to buy some credits
                  </Link>
                </p>
              </div>}

              <h3 className="text-xl text-center font-bold tracking-tight text-primary-500 pb-8">
                Select the model you want to use
              </h3>
              <div className="grid grid-cols-2 gap-4 sm:gap-8 pb-6">
                {modelOptions &&
                  modelOptions.map((model, index) => (
                    <div
                      key={index}
                      className={twMerge(
                        "flex flex-col max-w-sm p-4 bg-tertiary-800 border border-secondary-500 rounded-lg shadow hover:bg-tertiary-700 cursor-pointer",
                        selectedModelOption === index && "bg-tertiary-700",
                      )}
                      onClick={() => setSelectedModelOption(index)}
                    >
                      <h4 className="text-left mb-2 text-lg font-bold tracking-tight text-secondary-100">
                        {model.name}
                      </h4>
                      <p className="text-left text-sm text-secondary-200">
                        {model.description}
                      </p>
                    </div>
                  ))}
              </div>
              <div className="flex items-end justify-end">
                <Button
                  id="continue"
                  onClick={() => setCurrentStep(2)}
                  label="Continue"
                  className="mt-4"
                  disabled={
                    selectedModelOption === undefined ||
                    Number(amount) === 0
                  }
                />
              </div>
            </div>
          ) : currentStep === 2 ? (
            <div className="py-8 px-4">
              <h3 className="text-xl sm:text-2xl font-bold tracking-tight text-primary-500 pb-6">
                Proof request name and description
              </h3>
              <h2 className="tracking-tight text-secondary-200 pb-6">
                Give a name and a description to the proof request so you can
                identify it later.
              </h2>
              <div className="mb-6">
                <label
                  htmlFor="name"
                  className="block mb-2 text-sm font-medium text-secondary-100"
                >
                  Name
                </label>
                <input
                  type="name"
                  id="name"
                  className="bg-tertiary-800 border border-secondary-500 text-secondary-100 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5"
                  required
                  value={formData.name}
                  onChange={(e) =>
                    setFormData({ ...formData, name: e.target.value })
                  }
                />
              </div>
              <div className="mb-6">
                <label
                  htmlFor="description"
                  className="block mb-2 text-sm font-medium text-secondary-100"
                >
                  Description
                </label>
                <input
                  type="description"
                  id="description"
                  className="bg-tertiary-800 border border-secondary-500 text-secondary-100 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5"
                  required
                  value={formData.description}
                  onChange={(e) =>
                    setFormData({ ...formData, description: e.target.value })
                  }
                />
              </div>
              <div className="flex items-end justify-end">
                <Button
                  id="continue"
                  onClick={() => setCurrentStep(3)}
                  label="Continue"
                  className="mt-4"
                  disabled={
                    formData.name === undefined ||
                    formData.description === undefined ||
                    Number(amount) === 0
                  }
                />
              </div>
            </div>
          ) : (
            <div className="py-8 px-4">
              <h3 className="text-xl sm:text-2xl font-bold tracking-tight text-primary-500 pb-6">
                Json input
              </h3>
              <h2 className="tracking-tight text-secondary-200 pb-6">
                Insert a valid JSON input for model{" "}
                {modelOptions[selectedModelOption!].name}
              </h2>
              <JsonInput
                jsonString={formData?.jsonInput ?? ""}
                setJsonString={(jsonText) =>
                  setFormData({ ...formData, jsonInput: jsonText })
                }
              />
              <div className="mt-6 flex flex-col items-end justify-end">
                {formData?.jsonInput &&
                  formData?.jsonInput.length > 0 &&
                  !isValidJson(formData?.jsonInput!) && (
                    <p className="text-primary-500 text-sm mb-6">
                      Invalid JSON
                    </p>
                  )}
                <Button
                  id="send"
                  type="submit"
                  label="Compute Proof"
                  disabled={
                    !isValidJson(formData?.jsonInput ?? "") ||
                    Number(amount) === 0
                  }
                />
              </div>
            </div>
          )}
        </div>
      </form>
    </div>
  );
}
