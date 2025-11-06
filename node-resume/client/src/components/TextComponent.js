import React from "react";

const TextComponent = ({ text }) => {
  if (!text) return null;

  return (
    <ul style={{ padding: "5px", margin: 0 }}>
      {text.split(". ").filter(Boolean).map((sentence, index) => (
        <li key={index}>{sentence}.</li>
      ))}
    </ul>
  );
};

export default TextComponent;
