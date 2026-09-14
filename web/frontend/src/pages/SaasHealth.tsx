import { useState } from 'react';
import {
	Alert,
	Button,
	Card,
	Col,
	Form,
	InputNumber,
	Progress,
	Row,
	Space,
	Table,
	Tag,
	Typography,
	theme,
} from 'antd';
import {
	api,
	ApiError,
	type RagStatus,
	type SaasHealthRequest,
	type SaasHealthResponse,
	type SaasMetric,
} from '../lib/api';
import { AiPanel } from '../components/AiPanel';

const FIELDS: {
	key: keyof SaasHealthRequest;
	label: string;
	unit: string;
	example: number;
}[] = [
	{ key: 'arr', label: 'ARR', unit: '$', example: 2_000_000 },
	{ key: 'arr_growth_yoy', label: 'YoY ARR Growth', unit: '%', example: 120 },
	{ key: 'monthly_churn', label: 'Monthly Churn', unit: '%', example: 2.5 },
	{ key: 'net_revenue_retention', label: 'Net Revenue Retention', unit: '%', example: 110 },
	{ key: 'cac_payback_months', label: 'CAC Payback', unit: 'mo', example: 12 },
	{ key: 'gross_margin', label: 'Gross Margin', unit: '%', example: 75 },
	{ key: 'burn_rate_monthly', label: 'Monthly Net Burn', unit: '$/mo', example: 150_000 },
	{ key: 'cash_on_hand', label: 'Cash on Hand', unit: '$', example: 3_000_000 },
];

const STATUS_TAG: Record<RagStatus, { color: string; text: string }> = {
	GREEN: { color: 'success', text: 'Healthy' },
	AMBER: { color: 'warning', text: 'Watch' },
	RED: { color: 'error', text: 'At Risk' },
};

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

export default function SaasHealth() {
	const { token } = theme.useToken();
	const [form] = Form.useForm<SaasHealthRequest>();
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState<string | null>(null);
	const [result, setResult] = useState<SaasHealthResponse | null>(null);

	function fillExample() {
		form.setFieldsValue(
			Object.fromEntries(FIELDS.map((f) => [f.key, f.example])),
		);
	}

	async function submit(values: SaasHealthRequest) {
		setLoading(true);
		setError(null);
		try {
			setResult(await api.saasHealth(values));
		} catch (e) {
			setError(e instanceof ApiError ? e.message : 'Submission failed');
		} finally {
			setLoading(false);
		}
	}

	const regularMetrics = result?.metrics.filter((m) => m.key !== 'runway') ?? [];
	const runwayMetric = result?.metrics.find((m) => m.key === 'runway');

	const scoreColor = !result
		? token.colorText
		: result.score >= 70
			? token.colorSuccess
			: result.score >= 40
				? token.colorWarning
				: token.colorError;

	return (
		<div>
			<Typography.Title level={4} style={{ marginTop: 0 }}>
				SaaS Health
			</Typography.Title>
			<Typography.Paragraph type="secondary">
				Enter your core operating metrics to get RAG-rated evaluations and a cash runway
				estimate
			</Typography.Paragraph>

			<Row gutter={[16, 16]} align="top">
				<Col xs={24} xl={9}>
					<Card
						title="Input Metrics"
						extra={
							<Button size="small" onClick={fillExample}>
								Fill Sample Data
							</Button>
						}
					>
						<Form form={form} layout="vertical" onFinish={submit} size="middle">
							<Row gutter={12}>
								{FIELDS.map((f) => (
									<Col span={12} key={f.key}>
										<Form.Item
											name={f.key}
											label={f.label}
											rules={[{ required: true, message: 'Required' }]}
										>
											<InputNumber
												style={{ width: '100%' }}
												min={0}
												addonAfter={f.unit}
												placeholder="0"
											/>
										</Form.Item>
									</Col>
								))}
							</Row>
							{error && (
								<Alert type="error" showIcon message={error} style={{ marginBottom: 12 }} />
							)}
							<Button type="primary" htmlType="submit" loading={loading} block>
								Run Diagnostics
							</Button>
						</Form>
					</Card>
				</Col>

				<Col xs={24} xl={15}>
					{!result ? (
						<Card>
							<Typography.Paragraph type="secondary" style={{ textAlign: 'center', margin: 32 }}>
								Fill in the metrics on the left and submit — results will appear here
							</Typography.Paragraph>
						</Card>
					) : (
						<Space direction="vertical" size={16} style={{ width: '100%' }}>
							<Card>
								<Row gutter={24} align="middle">
									<Col flex="none">
										<Progress
											type="dashboard"
											size={120}
											percent={result.score}
											format={(p) => p ?? 0}
											strokeColor={scoreColor}
										/>
									</Col>
									<Col flex="auto">
										<Typography.Text strong>Health Score: {result.score}</Typography.Text>
										<Typography.Paragraph style={{ marginTop: 8, marginBottom: 0 }}>
											{result.summary}
										</Typography.Paragraph>
									</Col>
								</Row>
							</Card>

							{runwayMetric && (
								<Alert
									type={
										runwayMetric.status === 'GREEN'
											? 'success'
											: runwayMetric.status === 'AMBER'
												? 'warning'
												: 'error'
									}
									showIcon
									message={
										<>
											Cash Runway:{' '}
											{result.runway_months == null
												? '—'
												: `${result.runway_months} months`}
										</>
									}
									description={runwayMetric.recommendation}
								/>
							)}

							<Table<SaasMetric>
								rowKey="key"
								size="middle"
								dataSource={regularMetrics}
								pagination={false}
								columns={[
									{ title: 'Metric', dataIndex: 'label', width: 150 },
									{
										title: 'Value',
										key: 'value',
										width: 110,
										render: (_, m) =>
											m.value == null ? '—' : `${m.value} ${m.unit}`,
									},
									{
										title: 'Status',
										dataIndex: 'status',
										width: 90,
										render: (s: RagStatus) => (
											<Tag color={STATUS_TAG[s].color}>{STATUS_TAG[s].text}</Tag>
										),
									},
									{
										title: 'Thresholds',
										key: 'ranges',
										render: (_, m) => (
											<Typography.Text type="secondary" style={{ fontSize: 12 }}>
												GREEN {m.green_range} · AMBER {m.amber_range} · RED{' '}
												{m.red_range}
											</Typography.Text>
										),
									},
									{ title: 'Recommendation', dataIndex: 'recommendation' },
								]}
							/>

							<AiPanel tool="saas-health" result={result} runId={result.run_id} />
							<Disclaimer />
						</Space>
					)}
				</Col>
			</Row>
		</div>
	);
}
