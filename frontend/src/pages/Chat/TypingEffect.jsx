// TypingEffect.jsx
import { useEffect, useMemo, useRef, useState } from "react";

/**
 * TypingEffect
 * - text: 전체 텍스트
 * - interval: 타이핑 간격(ms)
 * - render: (partialText: string) => ReactNode  // 부분 문자열을 어떻게 렌더할지 (예: MarkdownRenderer)
 * - onDone: 타이핑 완료 시 호출
 * - preserveOnTextChange: 텍스트 변경 시 이전 진행상태 보존할지 (기본 false = 초기화)
 */
function TypingEffect({
  text = "",
  interval = 50,
  render,
  onDone,
  preserveOnTextChange = false,
}) {
  const [index, setIndex] = useState(0);
  const [done, setDone] = useState(false);
  const timerRef = useRef(null);

  // ✅ 유니코드 안전 타이핑(이모지/한글 자모 결합 등) — 브라우저 지원 시
  const segments = useMemo(() => {
    if (typeof Intl !== "undefined" && Intl.Segmenter) {
      const seg = new Intl.Segmenter("ko", { granularity: "grapheme" });
      return Array.from(seg.segment(text), (s) => s.segment);
    }
    // 폴백: 일반 char 분해
    return Array.from(text);
  }, [text]);

  // 텍스트가 바뀌면 기본값은 초기화 (preserveOnTextChange=false)
  useEffect(() => {
    if (!preserveOnTextChange) {
      setIndex(0);
      setDone(false);
    }
  }, [text, preserveOnTextChange]);

  useEffect(() => {
    if (done) return;
    if (index >= segments.length) {
      setDone(true);
      onDone?.();
      return;
    }

    timerRef.current = setTimeout(() => {
      setIndex((i) => i + 1);
    }, interval);

    return () => {
      clearTimeout(timerRef.current);
    };
  }, [index, segments.length, interval, done, onDone]);

  const displayedText = useMemo(
    () => segments.slice(0, index).join(""),
    [segments, index]
  );

  // render prop이 있으면 그걸로 표시 (예: <MarkdownRenderer content={displayedText} />)
  if (typeof render === "function") {
    return <>{render(displayedText)}</>;
  }

  // 기본 텍스트 렌더
  return <div>{displayedText}</div>;
}

export default TypingEffect;
