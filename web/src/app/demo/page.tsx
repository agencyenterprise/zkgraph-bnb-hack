"use client";

import Button from "@/components/button";
import { useChain } from "@/providers/chain";

import { useActiveAccount } from "thirdweb/react";
import { useEffect, useState } from "react";
import { toast } from "react-toastify";
import { isValidJson } from "@/utils/json";
import JsonInput from "@/components/json-input";

type Data = {
  name?: string;
  description?: string;
  jsonInput?: string;
};

export default function BuyPage() {
  const [formData, setFormData] = useState<Data>({});
  const [formErrors, setFormErrors] = useState<string[]>([]);
  const { client, escrowContract } = useChain();
  const activeAccount = useActiveAccount();

  useEffect(() => {
    if (formData.jsonInput && !isValidJson(formData.jsonInput)) {
      setFormErrors((prev) => Array.from(new Set([...prev, "Invalid JSON"])));
    } else {
      setFormErrors((prev) => prev.filter((error) => error !== "Invalid JSON"));
    }
  }, [formData.jsonInput]);

  const handleInference = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!client || !escrowContract || !activeAccount) {
      return;
    }

    if (!formData.name || !formData.description || !formData.jsonInput) {
      if (!formData.name) {
        setFormErrors((prev) =>
          Array.from(new Set([...prev, "Name is required"])),
        );
      }
      if (!formData.description) {
        setFormErrors((prev) =>
          Array.from(new Set([...prev, "Description is required"])),
        );
      }
      if (!formData.jsonInput) {
        setFormErrors((prev) =>
          Array.from(new Set([...prev, "JSON input is required"])),
        );
      }

      return;
    }

    try {
      const response = await fetch("/api/inference", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ formData }),
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
          <div className="mb-6">
            <label
              htmlFor="name"
              className="block mb-2 text-sm font-medium text-gray-900 dark:text-white"
            >
              Name
            </label>
            <input
              type="name"
              id="name"
              className="bg-[#1e1e1e] border border-[#1e1e1e] text-white text-sm rounded-lg focus:ring-white focus:border-white block w-full p-2.5 "
              value={formData.name}
              onChange={(e) =>
                setFormData({ ...formData, name: e.target.value })
              }
            />
          </div>
          <div className="mb-6">
            <label
              htmlFor="description"
              className="block mb-2 text-sm font-medium text-gray-900 dark:text-white"
            >
              Description
            </label>
            <input
              type="description"
              id="description"
              className="bg-[#1e1e1e] border border-[#1e1e1e] text-white text-sm rounded-lg focus:ring-white focus:border-white block w-full p-2.5 "
              value={formData.description}
              onChange={(e) =>
                setFormData({ ...formData, description: e.target.value })
              }
            />
          </div>

          <div className="mb-6">
            <h2 className="tracking-tight text-gray-100 pb-3">
              Insert a valid json input for the Iris model
            </h2>
            <JsonInput
              jsonString={formData?.jsonInput ?? ""}
              setJsonString={(jsonText) =>
                setFormData({ ...formData, jsonInput: jsonText })
              }
            />
          </div>

          {formErrors?.length > 0 && (
            <div className="mt-4 flex flex-col items-end justify-end">
              {formErrors.map((error) => (
                <p key={error} className="text-red-400 text-sm mb-1">
                  {error}
                </p>
              ))}
            </div>
          )}

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
