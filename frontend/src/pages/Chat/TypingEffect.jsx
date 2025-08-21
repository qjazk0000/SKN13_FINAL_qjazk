// TypingEffect.jsx

import { useEffect, useState } from "react";

function TypingEffect({ text = "" }) {

  const [displayedText, setDisplayedText] = useState("");
  const [index, setIndex] = useState(0);

  useEffect(() => {
    if (text && index < text.length) {
      const timer = setTimeout(() => {
        setDisplayedText((prev) => prev + text.charAt(index));
        setIndex((prev) => prev + 1);
      }, 50); // 50ms 간격으로 글자를 추가

      return () => clearTimeout(timer);
    }
  }, [index, text]);

  return <div>{displayedText}</div>;
}

export default TypingEffect;
