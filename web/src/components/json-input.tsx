"use client";

import dynamic from "next/dynamic";
import React from "react";

// Dynamically import the Monaco Editor to ensure it works with Next.js
const MonacoEditor = dynamic(() => import("@monaco-editor/react"), {
  ssr: false,
});

interface JsonInputProps {
  label?: string;
  jsonString: string;
  setJsonString: (value: string) => void;
}

const JsonInput: React.FC<JsonInputProps> = ({
  label,
  jsonString,
  setJsonString,
}) => {
  const handleJsonChange = (value: string | undefined) => {
    if (value !== undefined) {
      setJsonString(value);
    }
  };

  return (
    <div>
      {label && <h3>{label}</h3>}
      <MonacoEditor
        height="400px"
        defaultLanguage="json"
        theme="vs-dark"
        value={jsonString}
        onChange={handleJsonChange}
        options={{
          selectOnLineNumbers: true,
          automaticLayout: true,
        }}
      />
    </div>
  );
};

export default JsonInput;
