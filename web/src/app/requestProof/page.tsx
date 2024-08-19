"use client";

import Button from "@/components/button";
import { useChain } from "@/providers/chain";

import { useActiveAccount } from "thirdweb/react";
import { useState } from "react";
import { toast } from "react-toastify";
import { isValidJson } from "@/utils/json";
import JsonInput from "@/components/json-input";
import { useRouter } from "next/navigation";
import { twMerge } from 'tailwind-merge';
import Loading from "@/components/loading";

type Data = {
  name?: string;
  description?: string;
  jsonInput?: string;
};

const modelOptions = [
  {
    name: "Iris model",
    modelId: "iris_model",
    description: "This model generates a prediction on whether you are a human being or a ladybird",
  },
  {
    name: "Incoming model",
    description: "Incoming model",
  },
]

export default function BuyPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<Data>({});
  const [currentStep, setCurrentStep] = useState<number>(1);
  const [selectedModelOption, setSelectedModelOption] = useState<number | undefined>();
  const { client, escrowContract } = useChain();
  const activeAccount = useActiveAccount();

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
        console.log(message);
        toast.error(message + e);
      }
    } catch (error) {
      const message = "Error generating inference";
      console.log(message);
      toast.error(message + error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-gray-900 py-20 sm:py-32 min-h-screen">
      <form onSubmit={handleInference}>
        <div className="mx-auto max-w-xl lg:max-w-lg">
          <h2 className="text-3xl font-bold tracking-tight text-white pb-6 text-center mx-auto">
            Proof Request
          </h2>
          {
            loading ? (
              <div className="mb-6 flex justify-center">
                <Loading size="100px" />
              </div>
            ) : (
              <div className="mb-6 flex justify-center sm:justify-start">
                <Button
                  id={`button-submit`}
                  type="submit"
                  label={"Generate Inference"}
                />
              </div>
            ) || currentStep === 1 && (
              <>
                <h3 className="text-2xl font-bold tracking-tight text-white pb-6">
                  Select the model
                </h3>
                <div className="grid grid-cols-2 gap-8">
                  {
                    modelOptions && modelOptions.map((model, index) => (
                      <div
                        key={index}
                        className={twMerge(
                          "flex flex-col max-w-sm p-4 bg-white border border-gray-200 rounded-lg shadow hover:bg-gray-100 dark:bg-gray-800 dark:border-gray-700 dark:hover:bg-gray-700 cursor-pointer",
                          selectedModelOption === index && "bg-gray-100 dark:bg-gray-700"
                        )}
                        onClick={() => setSelectedModelOption(index)}
                      >
                        <h4 className="text-left mb-2 text-lg font-bold tracking-tight text-gray-900 dark:text-white">
                          {model.name}
                        </h4>
                        <p className="text-left text-sm text-gray-700 dark:text-gray-400">
                          {model.description}
                        </p>
                      </div>
                    ))
                  }
                </div>
                <div className="flex items-end justify-end">
                  <Button
                    id="continue"
                    onClick={() => setCurrentStep(2)}
                    label="Continue"
                    className="mt-4"
                    disabled={
                      selectedModelOption !== 0
                    }
                  />
                </div>
              </>
            )
            || currentStep === 2 && (
              <>
                <h3 className="text-2xl font-bold tracking-tight text-white pb-6">
                  Proof request name and description
                </h3>
                <h2 className="tracking-tight text-gray-100 pb-6">
                  Give a name and a description to the proof request so you can identify it later.
                </h2>
                <div className="mb-6">
                  <label htmlFor="name" className="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                    Name
                  </label>
                  <input
                    type="name"
                    id="name"
                    className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                    required
                    value={formData.name}
                    onChange={(e) =>
                      setFormData({ ...formData, name: e.target.value })
                    }
                  />
                </div>
                <div className="mb-6">
                  <label htmlFor="description" className="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                    Description
                  </label>
                  <input
                    type="description"
                    id="description"
                    className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
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
                      formData.description === undefined
                    }
                  />
                </div>
              </>
            )
            || currentStep === 3 && (
              <>
                <h3 className="text-2xl font-bold tracking-tight text-white pb-6">
                  Json input
                </h3>
                <h2 className="tracking-tight text-gray-100 pb-6">
                  Insert a valid json input for model {modelOptions[selectedModelOption!].name}
                </h2>
                <JsonInput
                  jsonString={formData?.jsonInput ?? ""}
                  setJsonString={(jsonText) =>
                    setFormData({ ...formData, jsonInput: jsonText })
                  }
                />
                <div className="mt-4 flex flex-col items-end justify-end">
                  {
                    formData?.jsonInput && formData?.jsonInput.length > 0 && !isValidJson(formData?.jsonInput!) &&
                    <p className="text-red-400 text-sm mb-1">Invalid JSON</p>
                  }
                  <Button
                    id="send"
                    type="submit"
                    label="Compute Proof"
                    disabled={
                      !isValidJson(formData?.jsonInput ?? "")
                    }
                  />
                </div>
              </>
            )
          }
        </div>
      </form>
    </div>
  );
}
