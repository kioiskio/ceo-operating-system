import { useEffect, useState } from 'react';
import { Alert, Skeleton, Tabs, Typography } from 'antd';
import { api, ApiError, type Framework } from '../lib/api';
import { Markdown } from '../components/Markdown';

export default function Frameworks() {
	const [frameworks, setFrameworks] = useState<Framework[] | null>(null);
	const [error, setError] = useState<string | null>(null);

	useEffect(() => {
		api
			.frameworks()
			.then((res) => setFrameworks(res.frameworks))
			.catch((e) => setError(e instanceof ApiError ? e.message : 'Failed to load'));
	}, []);

	return (
		<div>
			<Typography.Title level={4} style={{ marginTop: 0 }}>
				Frameworks
			</Typography.Title>
			<Typography.Paragraph type="secondary">
				Fundraising methodology and PMF validation frameworks
			</Typography.Paragraph>

			{error && <Alert type="error" showIcon message={error} />}
			{!frameworks && !error && <Skeleton active paragraph={{ rows: 10 }} />}

			{frameworks && (
				<Tabs
					items={frameworks.map((f) => ({
						key: f.id,
						label: f.title,
						children: <Markdown content={f.content} />,
					}))}
				/>
			)}
		</div>
	);
}
