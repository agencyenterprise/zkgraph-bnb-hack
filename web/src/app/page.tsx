"use client";

import Button from "@/components/button";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function Home() {
  const router = useRouter();
  return (
    <div className="mx-auto max-w-2xl py-16 sm:py-32 lg:py-36 px-4 ">
      <div className="hidden sm:mb-8 sm:flex sm:justify-center">
        <div className="relative rounded-full px-3 py-1 text-sm leading-6 text-gray-400 ring-1 ring-white/10 hover:ring-white/20">
          Public code and more techinical info{" "}
          <Link
            href="https://github.com/agencyenterprise/zkgraph-bnb-hack"
            className="font-semibold text-white"
          >
            <span className="absolute inset-0" aria-hidden="true" />
            Read more <span aria-hidden="true">&rarr;</span>
          </Link>
        </div>
      </div>
      <div className="text-center">
        <h1 className="text-2xl font-bold tracking-tight text-white sm:text-5xl">
          A ZKML framework based on the Virgo++/Libra protocol
        </h1>
        <p className="mt-6 text-lg leading-8 text-gray-300">
          This application implements on-chain verification using the linear
          prover time zk protocol Virgo++/Libra. It is designed to generate
          proofs for small ONNX graphs for MLP and Numpy computations.
        </p>
        <div className="mt-10 flex items-center justify-center gap-x-6">
          <Button
            id={`button-started`}
            type="button"
            label="Get started"
            onClick={() => {
              router.push("/demo");
            }}
          />
          <a
            href="/demo"
            className="text-sm font-semibold leading-6 text-white"
          >
            Learn more <span aria-hidden="true">→</span>
          </a>
        </div>
      </div>
    </div>
  );
}
