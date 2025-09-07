// src/pages/Chat/MarkdownRenderer.jsx
import hljs from "highlight.js";
import "highlight.js/styles/github.css"; // 테마 교체 가능 (atom-one-dark.css 등)
import Markdown from "markdown-to-jsx";
import { useEffect, useRef } from "react";

function CodeBlock({ className = "", children }) {
  const ref = useRef(null);

  useEffect(() => {
    if (ref.current) {
      ref.current.querySelectorAll("pre code").forEach((el) => {
        try {
          hljs.highlightElement(el);
        } catch {}
      });
    }
  }, [children]);

  const lang = (className || "").replace("lang-", "").replace("language-", "");
  return (
    <div className="relative group" ref={ref}>
      <pre className="rounded-lg bg-gray-900 text-gray-100 p-3 overflow-x-auto">
        <code className={lang ? `language-${lang}` : ""}>{children}</code>
      </pre>
      {lang && (
        <span className="absolute left-2 top-2 text-[10px] px-1.5 py-0.5 rounded bg-black/20">
          {lang}
        </span>
      )}
    </div>
  );
}

export default function MarkdownRenderer({ content = "" }) {
  return (
    <div className="prose prose-gray max-w-none break-words">
      <Markdown
        options={{
          // GFM 기능(표, 체크박스) 대부분 기본 지원
          forceBlock: true,
          overrides: {
            a: {
              component: (props) => {
                // 다운로드 링크인지 확인 (S3 퍼블릭 URL 또는 form/download 경로 포함)
                const isDownloadLink = props.href && (
                  props.href.includes('/api/chat/form/download/') || 
                  props.href.includes('.s3.ap-northeast-2.amazonaws.com/')
                );
                
                if (isDownloadLink) {
                  // URL에서 파일명 추출
                  let filename = '서식 파일';
                  
                  if (props.href.includes('/api/chat/form/download/')) {
                    // API 다운로드 링크인 경우
                    const urlParams = new URLSearchParams(props.href.split('?')[1]);
                    const s3Key = urlParams.get('s3_key');
                    filename = s3Key ? s3Key.split('/').pop() : '서식 파일';
                  } else if (props.href.includes('.s3.ap-northeast-2.amazonaws.com/')) {
                    // S3 퍼블릭 URL인 경우
                    const urlParts = props.href.split('/');
                    filename = urlParts[urlParts.length - 1] || '서식 파일';
                  }
                  
                  // React JSX 문법으로 <a> 태그 작성
                  return (
                    <a 
                      href={props.href}
                      download={filename}
                      title={filename}
                      style={{ 
                        cursor: 'pointer',
                        textDecoration: 'underline',
                        color: '#3b82f6',
                        display: 'inline-block'
                      }}
                    >
                      📄 [ 다운로드 &gt;. ]
                    </a>
                  );
                }
                
                // 일반 링크는 새 탭에서 열기
                return (
                  <a {...props} target="_blank" rel="noopener noreferrer">
                    {props.children || props.href}
                  </a>
                );
              },
            },
            code: {
              component: ({ className, children }) => {
                // 블록 코드: ```lang
                if (String(children).includes("\n")) {
                  return (
                    <CodeBlock className={className}>{children}</CodeBlock>
                  );
                }
                // 인라인 코드
                return (
                  <code className="px-1 py-0.5 rounded bg-gray-100">
                    {children}
                  </code>
                );
              },
            },
            table: {
              component: (props) => (
                <div className="overflow-x-auto">
                  <table {...props} />
                </div>
              ),
            },
          },
        }}
      >
        {content}
      </Markdown>
    </div>
  );
}
