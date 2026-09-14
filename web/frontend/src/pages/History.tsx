import { useEffect, useState } from 'react';
import {
	Alert,
	Button,
	Drawer,
	Popconfirm,
	Skeleton,
	Space,
	Table,
	Tag,
	Typography,
} from 'antd';
import {
	api,
	ApiError,
	type HistoryDetail,
	type HistoryRun,
} from '../lib/api';
import { formatTime } from '../lib/format';
import { Markdown } from '../components/Markdown';
import { TOOL_META } from '../lib/tool-meta';

function DetailContent({ detail }: { detail: HistoryDetail }) {
	const result = detail.result as {
		summary?: unknown;
		score?: number | null;
		percentage?: number;
		verdict?: string;
	} | null;

	const sections: string[] = [];
	if (result) {
		if (typeof result.summary === 'string') sections.push(result.summary);
		else if (result.summary && typeof result.summary === 'object') {
			sections.push('```json\n' + JSON.stringify(result.summary, null, 2) + '\n```');
		}
		if (typeof result.score === 'number') sections.push(`**Score:** ${result.score}`);
		if (typeof result.percentage === 'number')
			sections.push(`**Completion:** ${result.percentage.toFixed(0)}%`);
		if (result.verdict) sections.push(`**Verdict:** ${result.verdict}`);
	}
	if (sections.length === 0) {
		sections.push('```json\n' + JSON.stringify(result, null, 2).slice(0, 2000) + '\n```');
	}

	return (
		<div>
			<Typography.Title level={5}>Result Summary</Typography.Title>
			<Markdown content={sections.join('\n\n')} />
			{detail.ai_analysis && (
				<>
					<Typography.Title level={5} style={{ marginTop: 24 }}>
						AI Analysis
					</Typography.Title>
					<Markdown content={detail.ai_analysis} />
				</>
			)}
		</div>
	);
}

export default function History() {
	const [runs, setRuns] = useState<HistoryRun[] | null>(null);
	const [error, setError] = useState<string | null>(null);
	const [viewing, setViewing] = useState<HistoryDetail | 'loading' | null>(null);

	useEffect(() => {
		api
			.history()
			.then((res) => setRuns(res.runs))
			.catch((e) => setError(e instanceof ApiError ? e.message : 'Failed to load'));
	}, []);

	async function view(id: number) {
		setViewing('loading');
		try {
			setViewing(await api.historyDetail(id));
		} catch (e) {
			setViewing(null);
			setError(e instanceof ApiError ? e.message : 'Failed to load details');
		}
	}

	async function remove(id: number) {
		try {
			await api.historyDelete(id);
			setRuns((rs) => rs?.filter((r) => r.id !== id) ?? null);
		} catch (e) {
			setError(e instanceof ApiError ? e.message : 'Failed to delete');
		}
	}

	return (
		<div>
			<Typography.Title level={4} style={{ marginTop: 0 }}>
				Run History
			</Typography.Title>
			<Typography.Paragraph type="secondary">
				Past results from all tools
			</Typography.Paragraph>

			{error && (
				<Alert type="error" showIcon message={error} style={{ marginBottom: 16 }} />
			)}

			<Table<HistoryRun>
				rowKey="id"
				size="middle"
				loading={runs === null && !error}
				dataSource={runs ?? []}
				pagination={{ pageSize: 20, hideOnSinglePage: true }}
				columns={[
					{
						title: 'Tool',
						dataIndex: 'tool',
						width: 140,
						render: (tool: string) => {
							const meta = TOOL_META[tool];
							return <Tag color={meta?.color}>{meta?.label ?? tool}</Tag>;
						},
					},
					{ title: 'Title', dataIndex: 'title', ellipsis: true },
					{
						title: 'Score',
						dataIndex: 'score',
						width: 90,
						render: (score: number | null) => score ?? '—',
					},
					{
						title: 'Time',
						dataIndex: 'created_at',
						width: 180,
						render: formatTime,
					},
					{
						title: 'Actions',
						key: 'actions',
						width: 140,
						render: (_, run) => (
							<Space>
								<Button size="small" type="link" onClick={() => view(run.id)}>
									View
								</Button>
								<Popconfirm
									title="Delete this record?"
									okText="Delete"
									cancelText="Cancel"
									onConfirm={() => remove(run.id)}
								>
									<Button size="small" type="link" danger>
										Delete
									</Button>
								</Popconfirm>
							</Space>
						),
					},
				]}
			/>

			<Drawer
				title={viewing && viewing !== 'loading' ? viewing.title : 'Run Details'}
				open={viewing !== null}
				onClose={() => setViewing(null)}
				width={720}
			>
				{viewing === 'loading' || viewing === null ? (
					<Skeleton active paragraph={{ rows: 6 }} />
				) : (
					<DetailContent detail={viewing} />
				)}
			</Drawer>
		</div>
	);
}
