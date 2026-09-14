import { useEffect, useState } from 'react';
import { Button, Card, Col, Empty, Row, Table, Tag, Typography } from 'antd';
import {
	ArrowRightOutlined,
	AuditOutlined,
	LineChartOutlined,
	PieChartOutlined,
} from '@ant-design/icons';
import { Link } from 'react-router-dom';
import { api, type HistoryRun } from '../lib/api';
import { formatTime } from '../lib/format';
import { TOOL_META } from '../lib/tool-meta';

const TOOLS = [
	{
		to: '/saas-health',
		icon: <LineChartOutlined />,
		title: 'SaaS Health',
		desc: 'Enter 8 core metrics to get RAG status ratings, an overall health score, and a cash runway estimate.',
	},
	{
		to: '/equity',
		icon: <PieChartOutlined />,
		title: 'Equity Dilution',
		desc: 'Model multiple funding rounds and option pool expansions to visualize how founder ownership evolves.',
	},
	{
		to: '/deck-scorer',
		icon: <AuditOutlined />,
		title: 'Deck Scorer',
		desc: 'Self-check your deck against an investor-style 10-slide checklist and get a weighted score with priority fixes.',
	},
];

export default function Dashboard() {
	const [runs, setRuns] = useState<HistoryRun[] | null>(null);

	useEffect(() => {
		api
			.history()
			.then((res) => setRuns(res.runs.slice(0, 5)))
			.catch(() => setRuns([]));
	}, []);

	return (
		<div>
			<Typography.Title level={3} style={{ marginBottom: 4 }}>
				CEO Operating System
			</Typography.Title>
			<Typography.Paragraph type="secondary">
				A decision-support toolkit for founders — health diagnostics, equity modeling, and
				fundraising readiness in one place.
			</Typography.Paragraph>

			<Row gutter={[16, 16]}>
				{TOOLS.map((t) => (
					<Col key={t.to} xs={24} md={8}>
						<Card
							style={{ height: '100%' }}
							title={
								<span>
									{t.icon} {t.title}
								</span>
							}
							extra={
								<Link to={t.to}>
									<Button type="link" style={{ paddingInline: 0 }}>
										Open <ArrowRightOutlined />
									</Button>
								</Link>
							}
						>
							<Typography.Paragraph type="secondary" style={{ marginBottom: 0 }}>
								{t.desc}
							</Typography.Paragraph>
						</Card>
					</Col>
				))}
			</Row>

			<Card title="Recent Runs" style={{ marginTop: 16 }}>
				<Table<HistoryRun>
					rowKey="id"
					size="middle"
					loading={runs === null}
					dataSource={runs ?? []}
					pagination={false}
					locale={{ emptyText: <Empty description="No runs yet" /> }}
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
					]}
				/>
			</Card>
		</div>
	);
}
