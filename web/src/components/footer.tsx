import React from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faGithub } from "@fortawesome/free-brands-svg-icons";

const Footer = () => {
  return (
    <footer className="bg-black text-gray-400 py-8">
      <div className="relative py-5">
        <div className="absolute inset-0 flex items-center" aria-hidden="true">
          <div className="w-full h-0.5 bg-gradient-to-r from-black via-primary-500 to-black"></div>
        </div>
        <div className="relative flex justify-center">
          <span className="bg-black px-6 text-xl font-semibold leading-6 text-primary-500"></span>
        </div>
      </div>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex justify-between items-center">
        <div>
          <p>
            &copy; {new Date().getFullYear()} ZeroK Labs. All rights reserved.
          </p>
          <p className="text-sm mt-1">
            This project is open source and available under the MIT license.
          </p>
        </div>
        <div>
          <a
            href="https://github.com/agencyenterprise/zkgraph-bnb-hack"
            target="_blank"
            rel="noopener noreferrer"
            className="text-gray-400 hover:text-white transition-colors duration-300"
          >
            <FontAwesomeIcon icon={faGithub} size="2x" />
          </a>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
