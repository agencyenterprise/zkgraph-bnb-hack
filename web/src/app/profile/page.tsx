"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { toast } from "react-toastify";

type User = {
  address: string;
  api_token: string;
}

export default function Me() {
  const [user, setUser] = useState<User>();

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const response = await fetch(`/api/user`, {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
        });
        if (response.ok) {
          const data = await response.json();
          setUser(data);
        } else {
          toast.error("Failed to fetch user data");
        }

      } catch (error) {
        toast.error("Failed to fetch user data");
      }
    };

    fetchUserData();
  }, []);

  const onClickApiKey = () => async () => {
    if (!user) return
    navigator.clipboard.writeText(user.api_token ?? "").then(() => { })
  }

  const onGenerateApiToken = () => async () => {
    const response = await fetch(`/api/user/api_token`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
    });

    if (response.ok) {
      const data = await response.json();
      setUser({
        address: user!.address,
        api_token: data.api_token
      })
    } else {
      toast.error("Failed to fetch user data");
    }
  }

  return (
    <div className="bg-tertiary-900 py-12 sm:py-24 h-screen">
      <div className="mx-auto w-full sm:max-w-2xl px-4 sm:px-8">
        <div className="mx-auto text-center py-8">
          <h2 className="text-2xl font-bold tracking-tight text-secondary-100 sm:text-4xl">
            Profile
          </h2>
        </div>
        <section className="flex flex-col p-4 bg-tertiary-800 border border-secondary-500 rounded-lg shadow w-full">
          <div className="flex justify-between items-center space-x-2 mt-4 lg:mt-5" >
            <div
              className="min-w-16 text-sm font-medium text-secondary-100"
            >
              API Key
            </div>
            <button
              className="bg-tertiary-700 text-secondary-100 text-sm w-full p-0.5 tooltip cursor-pointer"
              data-tip="Copy to clipboard"
              onClick={onClickApiKey()}
            >
              {user?.api_token ? user.api_token : "API Key not created"}
            </button>
            <button
              type="submit"
              className="w-full text-white max-w-fit px-5 bg-primary-600 hover:bg-primary-700 focus:ring-4 focus:outline-none focus:ring-primary-300 font-medium rounded-lg text-sm py-2.5 text-center dark:bg-primary-600 dark:hover:bg-primary-700 dark:focus:ring-primary-800"
              onClick={onGenerateApiToken()}
            >
              {
                user?.api_token ? "Regenerate" : "Generate"
              }
            </button>
          </div>
        </section>
      </div>
    </div >
  );
}
