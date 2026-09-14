import { useEffect, useRef, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import mermaid from 'mermaid';
import { useTheme } from '../theme-context';

let mermaidSeq = 0;

function MermaidBlock({ chart }: { chart: string }) {
	const { resolved } = useTheme();
	const ref = useRef<HTMLDivElement>(null);
	const [error, setError] = useState<string | null>(null);

	useEffect(() => {
		let cancelled = false;
		mermaid.initialize({
			startOnLoad: false,
			theme: resolved === 'dark' ? 'dark' : 'default',
			securityLevel: 'loose',
		});
		mermaid
			.render(`mermaid-${++mermaidSeq}`, chart)
			.then(({ svg }) => {
				if (!cancelled && ref.current) ref.current.innerHTML = svg;
			})
			.catch((e) => {
				if (!cancelled) setError(String(e?.message ?? e));
			});
		return () => {
			cancelled = true;
		};
	}, [chart, resolved]);

	if (error) {
		return <pre>Mermaid rendering failed: {error}</pre>;
	}
	return <div ref={ref} className="mermaid-box" />;
}

export function Markdown({ content }: { content: string }) {
	return (
		<div className="md-body">
			<ReactMarkdown
				components={{
					code({ className, children }) {
						const text = String(children ?? '').replace(/\n$/, '');
						if (className === 'language-mermaid') {
							return <MermaidBlock chart={text} />;
						}
						return <code className={className}>{children}</code>;
					},
				}}
			>
				{content}
			</ReactMarkdown>
		</div>
	);
}
