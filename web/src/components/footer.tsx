import React from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faGithub } from "@fortawesome/free-brands-svg-icons";

const Footer = () => {
  return (
    <footer className="bg-black text-gray-400 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex justify-between items-center">
        <div>
          <p>
            &copy; Agency Enterprise, LLC dba ZeroK Labs{" "}
            {new Date().getFullYear()}
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
