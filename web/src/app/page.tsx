"use client";
import Button from "@/components/button";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faUpload,
  faDatabase,
  faShield,
  faCopy,
  faServer,
  faCoins,
  faMemory,
  faCheck,
} from "@fortawesome/free-solid-svg-icons";
import { useState } from "react";
import { title } from "process";

export default function Home() {
  const router = useRouter();
  const [copied, setCopied] = useState(false);

  const steps = [
    {
      icon: faUpload,
      title: "Upload Computational Graph",
      description:
        "Submit your ONNX graph to the zkGraph network using our Python SDK. Credits are required, but you can earn them by contributing computation power.",
    },
    {
      icon: faDatabase,
      title: "Distributed Proving",
      description:
        "Our network of prover nodes generates zero-knowledge proofs for your computation. Workers on the network are compensated for their participation.",
    },
    {
      icon: faShield,
      title: "On-chain Verification",
      description:
        "The proof can be easily verified on the Binance Smart Chain, ensuring trustless and efficient validation.",
    },
  ];

  const proverCommand =
    "ZKGRAPH_BSC_WALLET=yourwalletaddress; curl -sSL https://0k.wtf/zk-worker.sh | sh";

  const copyCommand = () => {
    navigator.clipboard.writeText(proverCommand);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const benefits = [
    {
      icon: faServer,
      title: "Lightweight Docker Setup",
      description:
        "Easy to configure on any machine without heavy hardware requirements.",
    },
    {
      icon: faMemory,
      title: "Low Resource Usage",
      description: "Minimal impact on your system's performance.",
    },
    {
      icon: faCoins,
      title: "Earn BSC Tokens",
      description:
        "Get rewarded for contributing to the network's computation power.",
    },
  ];

  return (
    <>
      <div className="relative mx-auto max-w-3xl py-16 sm:pt-48 sm:pb-36 px-2 text-secondary-100">
        <div className="hidden sm:mb-8 sm:flex sm:justify-center">
          <div className="relative rounded-full px-3 py-1 text-md leading-6 text-secondary-400 ring-1 ring-tertiary-600 hover:ring-tertiary-400">
            zkGraph for Binance Smart Chain Testnet is live!{" "}
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
            A <span className="text-primary-500">distributed zkML</span>{" "}
            framework
          </h1>
          <h2 className="text-xl sm:text-4xl">
            for trustless verifiable machine learning
          </h2>
          <p className="mt-6 text-lg leading-8 text-white">
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

      <div className="relative py-5">
        <div className="absolute inset-0 flex items-center" aria-hidden="true">
          <div className="w-full h-0.5 bg-gradient-to-r from-black via-primary-500 to-black"></div>
        </div>
        <div className="relative flex justify-center">
          <span className="bg-black px-6 text-xl font-semibold leading-6 text-primary-500">
            How It Works
          </span>
        </div>
      </div>

      <div className="py-16 sm:py-24">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl lg:text-center">
            <p className="mt-2 text-3xl font-bold tracking-tight text-secondary-100 sm:text-4xl">
              Prove &amp; Verify in Three Simple Steps
            </p>
            <p className="mt-6 text-lg leading-8 text-secondary-300">
              zkGraph simplifies the process of generating and verifying
              zero-knowledge proofs for your machine learning models and
              computations.
            </p>
          </div>
          <div className="mx-auto mt-16 max-w-2xl sm:mt-20 lg:mt-24 lg:max-w-none">
            <dl className="grid max-w-xl grid-cols-1 gap-x-8 gap-y-16 lg:max-w-none lg:grid-cols-3">
              {steps.map((step, stepIdx) => (
                <div key={stepIdx} className="flex flex-col">
                  <dt className="flex items-center gap-x-3 text-xl font-semibold leading-7 text-secondary-100">
                    <div className="rounded-lg bg-secondary-800 pb-2 pt-3 px-3 ring-1 ring-secondary-700">
                      <FontAwesomeIcon icon={step.icon} className="w-8 h-8" />
                    </div>
                    {step.title}
                  </dt>
                  <dd className="mt-4 flex flex-auto flex-col text-base leading-7 text-secondary-300">
                    <p className="flex-auto">{step.description}</p>
                  </dd>
                </div>
              ))}
            </dl>
          </div>
        </div>
      </div>

      <div id="node" className="relative py-5">
        <div className="absolute inset-0 flex items-center" aria-hidden="true">
          <div className="w-full h-0.5 bg-gradient-to-r from-black via-primary-500 to-black"></div>
        </div>
        <div className="relative flex justify-center">
          <span className="bg-black px-6 text-xl font-semibold leading-6 text-primary-500">
            Join the Network
          </span>
        </div>
      </div>

      <div className="py-16 sm:py-24">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl lg:text-center">
            <p className="mt-2 text-3xl font-bold tracking-tight text-secondary-100 sm:text-4xl">
              Run a Prover Node
            </p>
            <p className="mt-6 text-lg leading-8 text-secondary-300">
              Contribute to the zkGraph network by running a prover node.
              It&apos;s easy to set up and you can earn BSC tokens for your
              contribution. You&apos;ll need to have{" "}
              <span className="text-primary-500">
                <Link
                  href="https://docs.docker.com/get-docker/"
                  className="hover:text-primary-400"
                >
                  Docker
                </Link>
              </span>{" "}
              installed on your machine.
            </p>
          </div>
          <div className="mt-10 flex justify-center">
            <div className="relative">
              <pre className="bg-secondary-700 text-secondary-100 p-8 rounded-lg font-mono text-sm">
                {proverCommand}
              </pre>
              <button
                onClick={copyCommand}
                className="absolute top-2 right-2 text-secondary-400 hover:text-secondary-800"
                aria-label="Copy command"
              >
                <FontAwesomeIcon
                  icon={copied ? faCheck : faCopy}
                  className="w-5 h-5"
                />
              </button>
            </div>
          </div>
          <div className="mx-auto mt-16 max-w-2xl sm:mt-20 lg:mt-24 lg:max-w-none">
            <dl className="grid max-w-xl grid-cols-1 gap-x-8 gap-y-16 lg:max-w-none lg:grid-cols-3">
              {benefits.map((benefit, index) => (
                <div key={index} className="flex flex-col">
                  <dt className="flex items-center gap-x-3 text-xl font-semibold leading-7 text-white">
                    <div className="rounded-lg bg-primary-500/10 pb-2 pt-3 px-3 ring-1 ring-primary-500/20">
                      <FontAwesomeIcon
                        icon={benefit.icon}
                        className="h-8 w-8 text-primary-500"
                      />
                    </div>
                    {benefit.title}
                  </dt>
                  <dd className="mt-4 flex flex-auto flex-col text-base leading-7 text-gray-300">
                    <p className="flex-auto">{benefit.description}</p>
                  </dd>
                </div>
              ))}
            </dl>
          </div>
        </div>
      </div>
    </>
  );
}
