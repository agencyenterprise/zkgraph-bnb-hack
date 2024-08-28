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

export default function Home() {
  const router = useRouter();
  const [copied, setCopied] = useState(false);

  const steps = [
    {
      icon: faUpload,
      title: "Upload Model",
      description:
        "Submit your ONNX graph to the zkGraph network using our Python SDK.",
    },
    {
      icon: faDatabase,
      title: "Distributed Proving",
      description:
        "Our network of prover nodes generates zero-knowledge proofs for your computation.",
    },
    {
      icon: faShield,
      title: "On-chain Verification",
      description:
        "The proof is verified on the Binance Smart Chain, ensuring trustless and efficient validation.",
    },
  ];

  const proverCommand = "curl -sSL https://get.zkgraph.io | bash";

  const copyCommand = () => {
    navigator.clipboard.writeText(proverCommand);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const benefits = [
    { icon: faServer, text: "Lightweight setup - run on any machine" },
    { icon: faMemory, text: "Low memory usage - doesn't hog your resources" },
    { icon: faCoins, text: "Earn BSC tokens for contributing to the network" },
  ];

  return (
    <>
      <div className="relative mx-auto max-w-2xl py-20 sm:py-36 px-4 text-secondary-100">
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
            A <span className="text-primary-500">distributed zkML</span>{" "}
            framework
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

      {/* How it Works Section */}
      <div className="py-24 sm:py-32">
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
                  <dt className="flex items-center gap-x-3 text-base font-semibold leading-7 text-secondary-100">
                    <div className="rounded-lg bg-secondary-800 p-2 ring-1 ring-secondary-700">
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

      <div className="relative py-5">
        <div className="absolute inset-0 flex items-center" aria-hidden="true">
          <div className="w-full h-0.5 bg-gradient-to-r from-black via-primary-500 to-black"></div>
        </div>
        <div className="relative flex justify-center">
          <span className="bg-black px-6 text-xl font-semibold leading-6 text-primary-500">
            Join the Network
          </span>
        </div>
      </div>

      <div className="py-24 sm:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl lg:text-center">
            <p className="mt-2 text-3xl font-bold tracking-tight text-secondary-100 sm:text-4xl">
              Run a Prover Node
            </p>
            <p className="mt-6 text-lg leading-8 text-secondary-300">
              Contribute to the zkGraph network by running a prover node. It's
              easy to set up and you can earn BSC tokens for your contribution.
            </p>
          </div>
          <div className="mt-10 flex justify-center">
            <div className="relative">
              <pre className="bg-secondary-700 text-secondary-100 p-4 rounded-lg font-mono text-sm">
                {proverCommand}
              </pre>
              <button
                onClick={copyCommand}
                className="absolute top-2 right-2 text-secondary-400 hover:text-secondary-200"
                aria-label="Copy command"
              >
                <FontAwesomeIcon
                  icon={copied ? faCheck : faCopy}
                  className="w-5 h-5"
                />
              </button>
            </div>
          </div>
          <div className="mt-16 max-w-2xl mx-auto">
            <h3 className="text-xl font-semibold text-secondary-100 mb-6">
              Benefits of Running a Node
            </h3>
            <ul className="space-y-4">
              {benefits.map((benefit, index) => (
                <li
                  key={index}
                  className="flex items-center space-x-3 text-secondary-300"
                >
                  <FontAwesomeIcon
                    icon={benefit.icon}
                    className="w-5 h-5 text-primary-500"
                  />
                  <span>{benefit.text}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </>
  );
}
