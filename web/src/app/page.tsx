"use client";

import Button from "@/components/button";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function Home() {
  const router = useRouter();
  return (
    <div className="mx-auto max-w-2xl py-20 sm:py-36 px-4 text-secondary-100">
      <div className="hidden sm:mb-8 sm:flex sm:justify-center">
        <div className="relative rounded-full px-3 py-1 text-md leading-6 text-secondary-400 ring-1 ring-tertiary-600 hover:ring-tertiary-400">
          zkGraph for Binance Smart Chain is now available on{" "}
          <Link
            href="https://github.com/agencyenterprise/zkgraph-bnb-hack"
            className="font-semibold text-primary-500 hover:text-primary-400"
          >
            <span className="absolute inset-0" aria-hidden="true" />
            Github <span aria-hidden="true">&rarr;</span>
          </Link>
        </div>
      </div>
      <div className="text-center">
        <h1 className="text-2xl font-bold tracking-tight sm:text-5xl">
          A <span className="text-primary-500">distributed zkML</span> framework
        </h1>
        <h2 className="text-xl sm:text-4xl">
          for trustless verifiable machine learning
        </h2>
        <p className="mt-6 text-lg leading-8 text-secondary-200">
          zkGraph harnesses a network of distributed prover nodes to generate
          zero-knowledge proofs for ONNX graphs, starting with MLP and NumPy
          computations. By leveraging the Binance Smart Chain and the
          lightning-fast{" "}
          <Link
            className="text-primary-500 hover:text-primary-400"
            href="https://eprint.iacr.org/2019/317"
          >
            Libra
          </Link>{" "}
          protocol, we aim to bring unparalleled efficiency to on-chain
          verification.
        </p>
        <div className="mt-10 flex items-center justify-center gap-x-6">
          <Button
            className="text-xl"
            id={`button-started`}
            type="button"
            label="Interactive Demo"
            onClick={() => {
              router.push("/requestProof");
            }}
          />
          <a
            href="https://github.com/agencyenterprise/zkgraph-bnb-hack"
            className="text-sm font-semibold leading-6 text-secondary-100 hover:text-secondary-400"
          >
            Learn more <span aria-hidden="true">→</span>
          </a>
        </div>
      </div>
    </div>
  );
}
