import React from "react";

const TextComponent = ({ text }) => {

  const sentences = text.split(". ");
  const midIndex = Math.ceil(sentences.length / 2); // Find the middle index to split into two columns
  const firstColumn = sentences.slice(0, midIndex);
  const secondColumn = sentences.slice(midIndex);

  return (
    <div style={{ display: "flex", gap: "5px" }}> {/* Flexbox for two-column layout */}
      <ul style={{ padding: "5px" }}>
      {text.split(". ").map((sentence, index) => (
        <li key={index}>{sentence}.</li> // Add period back
      ))}
      </ul>
    </div>
  );
};

export default TextComponent;
