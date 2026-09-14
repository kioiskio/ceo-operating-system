import { useState } from 'react';
import {
	Alert,
	Button,
	Card,
	Col,
	Form,
	Input,
	InputNumber,
	Row,
	Space,
	Statistic,
	Table,
	Typography,
	theme,
} from 'antd';
import { DeleteOutlined, PlusOutlined } from '@ant-design/icons';
import {
	Area,
	AreaChart,
	CartesianGrid,
	Legend,
	ResponsiveContainer,
	Tooltip,
	XAxis,
	YAxis,
} from 'recharts';
import {
	api,
	ApiError,
	type EquityDilutionRequest,
	type EquityDilutionResponse,
	type EquityRound,
	type EquitySnapshot,
} from '../lib/api';
import { formatMoney, formatPct, formatShares } from '../lib/format';
import { AiPanel } from '../components/AiPanel';

const EXAMPLE: EquityDilutionRequest = {
	initial_shares: 10_000_000,
	founder_shares: 7_000_000,
	rounds: [
		{ name: 'Seed', amount_raised: 2_000_000, pre_money_valuation: 8_000_000, option_pool_pct: 10 },
		{ name: 'Series A', amount_raised: 10_000_000, pre_money_valuation: 30_000_000, option_pool_pct: 5 },
		{ name: 'Series B', amount_raised: 25_000_000, pre_money_valuation: 100_000_000, option_pool_pct: 0 },
	],
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

export default function Equity() {
	const { token } = theme.useToken();
	const [form] = Form.useForm<EquityDilutionRequest>();
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState<string | null>(null);
	const [result, setResult] = useState<EquityDilutionResponse | null>(null);

	async function submit(values: EquityDilutionRequest) {
		setLoading(true);
		setError(null);
		setResult(null);
		try {
			setResult(
				await api.equityDilution({
					...values,
					rounds: (values.rounds ?? []).filter((r) => r?.name?.trim()),
				}),
			);
		} catch (e) {
			setError(e instanceof ApiError ? e.message : 'Submission failed');
		} finally {
			setLoading(false);
		}
	}

	const chartData =
		result?.snapshots.map((s) => ({
			stage: s.stage,
			Founders: s.founder_pct,
			Others: s.others_pct,
			Investors: s.cumulative_investor_pct,
			'Option Pool': s.option_pool_pct,
		})) ?? [];

	return (
		<div>
			<Typography.Title level={4} style={{ marginTop: 0 }}>
				Equity Dilution
			</Typography.Title>
			<Typography.Paragraph type="secondary">
				Model how funding rounds and option pool expansions affect founder ownership, round
				by round
			</Typography.Paragraph>

			<Row gutter={[16, 16]} align="top">
				<Col xs={24} xl={10}>
					<Card
						title="Funding Parameters"
						extra={<Button size="small" onClick={() => form.setFieldsValue(EXAMPLE)}>Fill Sample Data</Button>}
					>
						<Form
							form={form}
							layout="vertical"
							onFinish={submit}
							initialValues={{
								initial_shares: 10_000_000,
								founder_shares: 7_000_000,
								rounds: [
									{
										name: 'Seed',
										amount_raised: 0,
										pre_money_valuation: 0,
										option_pool_pct: 0,
									},
								],
							}}
						>
							<Row gutter={12}>
								<Col span={12}>
									<Form.Item
										name="initial_shares"
										label="Initial Total Shares"
										rules={[{ required: true, message: 'Required' }]}
									>
										<InputNumber style={{ width: '100%' }} min={0} addonAfter="shares" />
									</Form.Item>
								</Col>
								<Col span={12}>
									<Form.Item
										name="founder_shares"
										label="Founder Shares"
										rules={[{ required: true, message: 'Required' }]}
									>
										<InputNumber style={{ width: '100%' }} min={0} addonAfter="shares" />
									</Form.Item>
								</Col>
							</Row>

							<Form.List name="rounds">
								{(fields, { add, remove }) => (
									<>
										{fields.map((field) => (
											<Card
												key={field.key}
												size="small"
												style={{ marginBottom: 12 }}
												title={
													<Form.Item
														name={[field.name, 'name']}
														noStyle
														rules={[{ required: true, message: 'Required' }]}
													>
														<Input
															variant="borderless"
															placeholder={`Round ${field.name + 1}`}
															style={{ fontWeight: 600, width: 140 }}
														/>
													</Form.Item>
												}
												extra={
													<Button
														type="text"
														size="small"
														danger
														icon={<DeleteOutlined />}
														onClick={() => remove(field.name)}
														aria-label="Remove round"
													/>
												}
											>
												<Row gutter={8}>
													<Col span={8}>
														<Form.Item
															name={[field.name, 'amount_raised']}
															label="Amount Raised"
															rules={[{ required: true, message: 'Required' }]}
															style={{ marginBottom: 0 }}
														>
															<InputNumber style={{ width: '100%' }} min={0} addonBefore="$" />
														</Form.Item>
													</Col>
													<Col span={8}>
														<Form.Item
															name={[field.name, 'pre_money_valuation']}
															label="Pre-money"
															rules={[{ required: true, message: 'Required' }]}
															style={{ marginBottom: 0 }}
														>
															<InputNumber style={{ width: '100%' }} min={0} addonBefore="$" />
														</Form.Item>
													</Col>
													<Col span={8}>
														<Form.Item
															name={[field.name, 'option_pool_pct']}
															label="Option Pool"
															rules={[{ required: true, message: 'Required' }]}
															style={{ marginBottom: 0 }}
														>
															<InputNumber style={{ width: '100%' }} min={0} max={100} addonAfter="%" />
														</Form.Item>
													</Col>
												</Row>
											</Card>
										))}
										<Button
											block
											type="dashed"
											icon={<PlusOutlined />}
											onClick={() =>
												add({
													name: `Round ${String.fromCharCode(65 + fields.length)}`,
													amount_raised: 0,
													pre_money_valuation: 0,
													option_pool_pct: 0,
												} satisfies EquityRound)
											}
											style={{ marginBottom: 16 }}
										>
											Add Round
										</Button>
									</>
								)}
							</Form.List>

							{error && (
								<Alert type="error" showIcon message={error} style={{ marginBottom: 12 }} />
							)}
							<Button type="primary" htmlType="submit" loading={loading} block>
								Run Simulation
							</Button>
						</Form>
					</Card>
				</Col>

				<Col xs={24} xl={14}>
					{!result ? (
						<Card>
							<Typography.Paragraph type="secondary" style={{ textAlign: 'center', margin: 32 }}>
								Configure the initial structure and funding rounds, then submit to
								visualize the dilution
							</Typography.Paragraph>
						</Card>
					) : (
						<Space direction="vertical" size={16} style={{ width: '100%' }}>
							<Card>
								<Row gutter={24}>
									<Col xs={24} sm={8}>
										<Statistic
											title="Founder Ownership"
											value={`${formatPct(result.summary.initial_founder_pct)} → ${formatPct(result.summary.final_founder_pct)}`}
										/>
									</Col>
									<Col xs={12} sm={8}>
										<Statistic
											title="Dilution"
											value={result.summary.dilution_pp}
											precision={1}
											suffix="pp"
											valueStyle={{ color: token.colorError }}
										/>
									</Col>
									<Col xs={12} sm={8}>
										<Statistic
											title="Ownership Retained"
											value={result.summary.retention_pct}
											precision={1}
											suffix="%"
										/>
									</Col>
								</Row>
							</Card>

							<Card title="Ownership Structure by Stage">
								<ResponsiveContainer width="100%" height={280}>
									<AreaChart data={chartData} margin={{ top: 4, right: 8, left: -16, bottom: 0 }}>
										<CartesianGrid stroke={token.colorBorderSecondary} vertical={false} />
										<XAxis
											dataKey="stage"
											tick={{ fill: token.colorTextSecondary, fontSize: 12 }}
											axisLine={{ stroke: token.colorBorder }}
											tickLine={false}
										/>
										<YAxis
											tick={{ fill: token.colorTextSecondary, fontSize: 12 }}
											axisLine={false}
											tickLine={false}
											tickFormatter={(v: number) => `${v}%`}
										/>
										<Tooltip
											contentStyle={{
												background: token.colorBgElevated,
												border: `1px solid ${token.colorBorderSecondary}`,
												borderRadius: token.borderRadiusLG,
												fontSize: 12,
												color: token.colorText,
											}}
											formatter={(value: number | string | (string | number)[]) =>
												`${Number(Array.isArray(value) ? value[0] : value).toFixed(1)}%`
											}
										/>
										<Legend wrapperStyle={{ fontSize: 12 }} />
										<Area type="monotone" dataKey="Founders" stackId="1" stroke={token.colorSuccess} fill={token.colorSuccess} fillOpacity={0.55} />
										<Area type="monotone" dataKey="Others" stackId="1" stroke={token.colorPrimary} fill={token.colorPrimary} fillOpacity={0.55} />
										<Area type="monotone" dataKey="Investors" stackId="1" stroke={token.colorWarning} fill={token.colorWarning} fillOpacity={0.55} />
										<Area type="monotone" dataKey="Option Pool" stackId="1" stroke={token.colorError} fill={token.colorError} fillOpacity={0.55} />
									</AreaChart>
								</ResponsiveContainer>
							</Card>

							<Card title="Cap Table">
								<Table<EquitySnapshot>
									rowKey="stage"
									size="middle"
									dataSource={result.snapshots}
									pagination={false}
									scroll={{ x: 760 }}
									columns={[
										{ title: 'Stage', dataIndex: 'stage', fixed: 'left', width: 110 },
										{
											title: 'Total Shares',
											dataIndex: 'total_shares',
											align: 'right',
											render: formatShares,
										},
										{
											title: 'Founders',
											dataIndex: 'founder_pct',
											align: 'right',
											render: (v: number) => formatPct(v),
										},
										{
											title: 'Others',
											dataIndex: 'others_pct',
											align: 'right',
											render: (v: number) => formatPct(v),
										},
										{
											title: 'Investors (cum.)',
											dataIndex: 'cumulative_investor_pct',
											align: 'right',
											render: (v: number) => formatPct(v),
										},
										{
											title: 'Option Pool',
											dataIndex: 'option_pool_pct',
											align: 'right',
											render: (v: number) => formatPct(v),
										},
										{
											title: 'Price per Share',
											dataIndex: 'price_per_share',
											align: 'right',
											render: (v: number | null) =>
												v == null ? '—' : `$${v.toFixed(4)}`,
										},
										{
											title: 'Post-money',
											dataIndex: 'post_money',
											align: 'right',
											render: formatMoney,
										},
									]}
								/>
							</Card>

							<AiPanel tool="equity-dilution" result={result} runId={result.run_id} />
							<Disclaimer />
						</Space>
					)}
				</Col>
			</Row>
		</div>
	);
}
