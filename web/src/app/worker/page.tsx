"use client";

import Button from "@/components/button";

export default function WorkerPage() {
  return (
    <div className="bg-tertiary-900 py-16 sm:py-32 min-h-screen">
      <div className="mx-auto max-w-7xl px-6 sm:px-8">
        <div className="mx-auto max-w-4xl text-center">
          <h2 className="mx-auto text-4xl font-bold tracking-tight text-secondary-100 sm:text-4xl py-6">
            Earn Money by Running Our Python Worker
          </h2>
          <p className="mt-6 max-w-2xl text-center text-lg leading-8 text-secondary-200 mx-auto">
            Follow the steps below to start earning by running computations for
            proof generation. You can monitor your progress and earnings in real
            time.
          </p>
        </div>

        <div className="mt-12 sm:mt-16 grid grid-cols-1 sm:grid-cols-2 gap-8 bg-tertiary-800 rounded-lg shadow-lg p-4">
          <div className=" p-6 ">
            <h3 className="text-2xl font-bold tracking-tight text-primary-500 text-center sm:text-left">
              Step-by-Step Tutorial
            </h3>
            <ol className="mt-6 space-y-4 text-lg leading-8 text-secondary-200">
              <li>
                1. Download our Python executable and install it on your system.
              </li>
              <li>
                2. Open the executable, which will launch a simple interface.
              </li>
              <li>
                3. Use the interface to start or pause the worker at any time.
              </li>
              <li>
                4. The interface displays the number of proofs you&apos;ve
                computed and your earnings in real time.
              </li>
              <li>
                5. Earnings are updated live, and you can view them on a
                graphical chart below.
              </li>
              <li>
                6. Once you&apos;re done, simply close the interface to stop the
                worker.
              </li>
            </ol>
          </div>

          <div className="p-6">
            <img
              src="https://i.pinimg.com/736x/bf/42/dd/bf42dd53cd548e99aa910a2ac1e5fd12.jpg"
              alt="Worker Inteface"
            ></img>
            <div className="mt-6 flex flex-col items-center w-full">
              <Button
                id="toggle-worker"
                label={"Download Executable"}
                className="mx-auto"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
