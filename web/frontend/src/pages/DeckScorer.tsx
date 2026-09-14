import { useEffect, useState } from 'react';
import {
	Alert,
	Button,
	Card,
	Checkbox,
	Collapse,
	Progress,
	Skeleton,
	Space,
	Statistic,
	Table,
	Tag,
	Typography,
	Row,
	Col,
} from 'antd';
import { DownloadOutlined } from '@ant-design/icons';
import {
	api,
	ApiError,
	type DeckCriteriaResponse,
	type DeckScoreResponse,
} from '../lib/api';
import { AiPanel } from '../components/AiPanel';

function verdictTag(verdict: string) {
	const v = verdict.toUpperCase();
	if (v.includes('NOT')) return <Tag color="error">{verdict}</Tag>;
	if (v.includes('READY')) return <Tag color="success">{verdict}</Tag>;
	return <Tag color="warning">{verdict}</Tag>;
}

function Disclaimer() {
	return (
		<Typography.Paragraph
			type="secondary"
			style={{ textAlign: 'center', fontSize: 12, marginTop: 24 }}
		>
			Decision support only — not legal, tax, or investment advice.
		</Typography.Paragraph>
	);
}

export default function DeckScorer() {
	const [criteria, setCriteria] = useState<DeckCriteriaResponse | null>(null);
	const [loadError, setLoadError] = useState<string | null>(null);
	const [responses, setResponses] = useState<boolean[][]>([]);
	const [submitting, setSubmitting] = useState(false);
	const [error, setError] = useState<string | null>(null);
	const [result, setResult] = useState<DeckScoreResponse | null>(null);

	useEffect(() => {
		api
			.deckCriteria()
			.then((res) => {
				setCriteria(res);
				setResponses(res.slides.map((s) => s.criteria.map(() => false)));
			})
			.catch((e) =>
				setLoadError(e instanceof ApiError ? e.message : 'Failed to load criteria'),
			);
	}, []);

	const total = responses.flat().length;
	const answered = responses.flat().filter(Boolean).length;

	function setSlideChecks(slideIndex: number, checkedValues: string[]) {
		setResponses((rs) =>
			rs.map((arr, i) =>
				i === slideIndex && criteria
					? criteria.slides[i].criteria.map((c) => checkedValues.includes(c))
					: arr,
			),
		);
	}

	async function submit() {
		setSubmitting(true);
		setError(null);
		try {
			setResult(await api.deckScore({ responses }));
		} catch (e) {
			setError(e instanceof ApiError ? e.message : 'Submission failed');
		} finally {
			setSubmitting(false);
		}
	}

	function exportJson() {
		if (!result) return;
		const blob = new Blob([JSON.stringify(result, null, 2)], {
			type: 'application/json',
		});
		const url = URL.createObjectURL(blob);
		const a = document.createElement('a');
		a.href = url;
		a.download = `deck-score-${result.run_id ?? 'result'}.json`;
		a.click();
		URL.revokeObjectURL(url);
	}

	return (
		<div>
			<Typography.Title level={4} style={{ marginTop: 0 }}>
				Deck Scorer
			</Typography.Title>
			<Typography.Paragraph type="secondary">
				Self-check your fundraising deck against investor review criteria, slide by slide
			</Typography.Paragraph>

			{loadError && <Alert type="error" showIcon message={loadError} />}
			{!criteria && !loadError && <Skeleton active paragraph={{ rows: 8 }} />}

			{criteria && (
				<Card
					title="Checklist"
					extra={
						<Space size={16}>
							<span style={{ minWidth: 200, display: 'inline-block' }}>
								<Progress
									percent={total ? Math.round((answered / total) * 100) : 0}
									size="small"
									format={() => `${answered}/${total}`}
								/>
							</span>
							<Button type="primary" onClick={submit} loading={submitting}>
								Score My Deck
							</Button>
						</Space>
					}
				>
					<Collapse
						defaultActiveKey={criteria.slides.map((_, i) => String(i))}
						items={criteria.slides.map((slide, si) => ({
							key: String(si),
							label: (
								<Space>
									{`${si + 1}. ${slide.name}`}
									<Tag>Weight ×{slide.weight}</Tag>
								</Space>
							),
							children: (
								<Checkbox.Group
									style={{ display: 'flex', flexDirection: 'column', gap: 8 }}
									options={slide.criteria.map((c) => ({ label: c, value: c }))}
									value={slide.criteria.filter((_, ci) => responses[si]?.[ci])}
									onChange={(values) => setSlideChecks(si, values as string[])}
								/>
							),
						}))}
					/>
				</Card>
			)}

			{error && <Alert type="error" showIcon message={error} style={{ marginTop: 16 }} />}

			{result && (
				<Space direction="vertical" size={16} style={{ width: '100%', marginTop: 16 }}>
					<Card
						title="Results"
						extra={
							<Button icon={<DownloadOutlined />} onClick={exportJson}>
								Export JSON
							</Button>
						}
					>
						<Row gutter={24} align="middle">
							<Col flex="none">
								<Statistic
									title="Weighted Score"
									value={result.score}
									suffix={`/ ${result.max_score}`}
								/>
							</Col>
							<Col flex="auto">
								<Progress percent={Math.round(result.percentage)} />
								<Space style={{ marginTop: 8 }}>
									{verdictTag(result.verdict)}
									<Typography.Text type="secondary">
										{result.verdict_message}
									</Typography.Text>
								</Space>
							</Col>
						</Row>
					</Card>

					<Card title="Slide Breakdown">
						<Table
							rowKey="slide"
							size="middle"
							dataSource={result.slides}
							pagination={false}
							columns={[
								{ title: 'Slide', dataIndex: 'slide', width: 160 },
								{
									title: 'Weight',
									dataIndex: 'weight',
									width: 90,
									render: (w: number) => <Tag>×{w}</Tag>,
								},
								{
									title: 'Passed',
									key: 'passed',
									width: 90,
									render: (_, s) => `${s.passed}/${s.total}`,
								},
								{
									title: 'Completion',
									dataIndex: 'percentage',
									width: 160,
									render: (p: number) => (
										<Progress
											percent={Math.round(p)}
											size="small"
											status={p >= 80 ? 'success' : p >= 50 ? 'normal' : 'exception'}
										/>
									),
								},
								{
									title: 'Missed Criteria',
									dataIndex: 'missed_criteria',
									render: (missed: string[]) =>
										missed.length === 0 ? (
											<Typography.Text type="secondary">None</Typography.Text>
										) : (
											<ul style={{ margin: 0, paddingInlineStart: 18 }}>
												{missed.map((m, i) => (
													<li key={i}>{m}</li>
												))}
											</ul>
										),
								},
							]}
						/>
					</Card>

					{result.priority_fixes.length > 0 && (
						<Card title="Priority Fixes">
							<Table
								rowKey="slide"
								size="middle"
								dataSource={result.priority_fixes}
								pagination={false}
								columns={[
									{
										title: '#',
										key: 'rank',
										width: 50,
										render: (_, __, i) => i + 1,
									},
									{ title: 'Slide', dataIndex: 'slide', width: 160 },
									{
										title: 'Weight',
										dataIndex: 'weight',
										width: 90,
										render: (w: number) => <Tag color="warning">×{w}</Tag>,
									},
									{
										title: 'Items to Fix',
										dataIndex: 'missed',
										render: (missed: string[]) => (
											<ul style={{ margin: 0, paddingInlineStart: 18 }}>
												{missed.map((m, i) => (
													<li key={i}>{m}</li>
												))}
											</ul>
										),
									},
								]}
							/>
						</Card>
					)}

					<AiPanel tool="deck-score" result={result} runId={result.run_id} />
					<Disclaimer />
				</Space>
			)}
		</div>
	);
}
