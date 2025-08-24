// components/MarkdownRenderer.jsx
import "highlight.js/styles/github.css"; // 코드 하이라이트 테마 (다른 스타일로 교체 가능)
import ReactMarkdown from "react-markdown";
import rehypeHighlight from "rehype-highlight";
import remarkGfm from "remark-gfm";

export default function MarkdownRenderer({ content }) {
  return (
    <div className="prose prose-gray max-w-none break-words">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeHighlight]}
        components={{
          a: (props) => (
            <a {...props} target="_blank" rel="noopener noreferrer" />
          ),
          code: ({ inline, className, children, ...rest }) => {
            if (inline) {
              return (
                <code
                  className="px-1 py-0.5 rounded bg-gray-100 text-red-500"
                  {...rest}
                >
                  {children}
                </code>
              );
            }
            return (
              <pre className="rounded-lg bg-gray-900 text-gray-100 p-3 overflow-x-auto">
                <code className={className}>{children}</code>
              </pre>
            );
          },
          table: (props) => (
            <div className="overflow-x-auto">
              <table {...props} />
            </div>
          ),
        }}
      >
        {content || ""}
      </ReactMarkdown>
    </div>
  );
}
