import { useState } from 'react';
import { Alert, Button, Skeleton } from 'antd';
import { RobotOutlined } from '@ant-design/icons';
import { Link } from 'react-router-dom';
import { api, ApiError, type ToolName } from '../lib/api';
import { isLlmConfigured, loadLlmConfig } from '../lib/llm-config';
import { Markdown } from './Markdown';

export function AiPanel({
	tool,
	result,
	runId,
}: {
	tool: ToolName;
	result: object;
	runId: number | null;
}) {
	const [loading, setLoading] = useState(false);
	const [analysis, setAnalysis] = useState<string | null>(null);
	const [error, setError] = useState<string | null>(null);

	const config = loadLlmConfig();

	if (!isLlmConfigured(config)) {
		return (
			<Alert
				style={{ marginTop: 24 }}
				type="info"
				showIcon
				message="LLM is not configured — AI deep analysis is unavailable"
				action={
					<Link to="/settings">
						<Button size="small">Go to Settings</Button>
					</Link>
				}
			/>
		);
	}

	async function analyze() {
		setLoading(true);
		setError(null);
		try {
			const res = await api.llmAnalyze({
				base_url: config.base_url,
				api_key: config.api_key,
				model: config.model,
				tool,
				result,
				run_id: runId,
			});
			setAnalysis(res.analysis);
		} catch (e) {
			setError(e instanceof ApiError ? e.message : 'AI analysis request failed');
		} finally {
			setLoading(false);
		}
	}

	return (
		<div style={{ marginTop: 24 }}>
			{!analysis && !loading && (
				<Button icon={<RobotOutlined />} onClick={analyze}>
					AI Deep Analysis
				</Button>
			)}
			{loading && (
				<>
					<p style={{ marginBottom: 12, color: 'inherit', opacity: 0.65 }}>
						Analyzing results with the LLM…
					</p>
					<Skeleton active paragraph={{ rows: 5 }} title={false} />
				</>
			)}
			{error && <Alert type="error" showIcon message={error} />}
			{analysis && (
				<div className="md-body">
					<Markdown content={analysis} />
				</div>
			)}
		</div>
	);
}
