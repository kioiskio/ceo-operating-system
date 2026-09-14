import { useEffect, useState } from 'react';
import { Alert, App, Button, Card, Skeleton, Space, Typography } from 'antd';
import { CheckOutlined, CopyOutlined, DownloadOutlined } from '@ant-design/icons';
import { api, ApiError, type Template } from '../lib/api';
import { Markdown } from '../components/Markdown';

export default function Templates() {
	const { message } = App.useApp();
	const [templates, setTemplates] = useState<Template[] | null>(null);
	const [error, setError] = useState<string | null>(null);
	const [copiedId, setCopiedId] = useState<string | null>(null);

	useEffect(() => {
		api
			.templates()
			.then((res) => setTemplates(res.templates))
			.catch((e) => setError(e instanceof ApiError ? e.message : 'Failed to load'));
	}, []);

	async function copy(t: Template) {
		try {
			await navigator.clipboard.writeText(t.content);
			setCopiedId(t.id);
			setTimeout(() => setCopiedId(null), 1500);
		} catch {
			message.error('Copy failed — check browser clipboard permissions');
		}
	}

	function download(t: Template) {
		const blob = new Blob([t.content], { type: 'text/markdown;charset=utf-8' });
		const url = URL.createObjectURL(blob);
		const a = document.createElement('a');
		a.href = url;
		a.download = t.filename;
		a.click();
		URL.revokeObjectURL(url);
	}

	return (
		<div>
			<Typography.Title level={4} style={{ marginTop: 0 }}>
				Templates
			</Typography.Title>
			<Typography.Paragraph type="secondary">
				Ready-to-copy fundraising and operations document templates
			</Typography.Paragraph>

			{error && <Alert type="error" showIcon message={error} />}
			{!templates && !error && <Skeleton active paragraph={{ rows: 10 }} />}

			<Space direction="vertical" size={16} style={{ width: '100%' }}>
				{templates?.map((t) => (
					<Card
						key={t.id}
						title={t.title}
						extra={
							<Space>
								<Button
									size="small"
									icon={copiedId === t.id ? <CheckOutlined /> : <CopyOutlined />}
									onClick={() => copy(t)}
								>
									{copiedId === t.id ? 'Copied' : 'Copy'}
								</Button>
								<Button
									size="small"
									icon={<DownloadOutlined />}
									onClick={() => download(t)}
								>
									Download .md
								</Button>
							</Space>
						}
					>
						<Typography.Text type="secondary" style={{ fontSize: 12 }}>
							{t.filename}
						</Typography.Text>
						<Markdown content={t.content} />
					</Card>
				))}
			</Space>
		</div>
	);
}
