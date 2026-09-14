import { useState } from 'react';
import { App, Button, Card, Form, Input, Typography } from 'antd';
import { api, ApiError } from '../lib/api';
import {
	DEFAULT_LLM_CONFIG,
	loadLlmConfig,
	saveLlmConfig,
	type LlmConfig,
} from '../lib/llm-config';

export default function Settings() {
	const { message } = App.useApp();
	const [form] = Form.useForm<LlmConfig>();
	const [testing, setTesting] = useState(false);

	async function test() {
		const config = form.getFieldsValue();
		setTesting(true);
		try {
			const res = await api.llmTest(config);
			if (res.ok) message.success(res.message);
			else message.error(res.message);
		} catch (e) {
			message.error(e instanceof ApiError ? e.message : 'Test request failed');
		} finally {
			setTesting(false);
		}
	}

	return (
		<div>
			<Typography.Title level={4} style={{ marginTop: 0 }}>
				Settings
			</Typography.Title>
			<Typography.Paragraph type="secondary">
				Configure the LLM used for AI deep analysis
			</Typography.Paragraph>

			<Card title="LLM Configuration" style={{ maxWidth: 560 }}>
				<Form<LlmConfig>
					form={form}
					layout="vertical"
					initialValues={loadLlmConfig()}
					onValuesChange={(_, values) => saveLlmConfig(values)}
				>
					<Form.Item
						name="base_url"
						label="Base URL"
						rules={[{ required: true, message: 'Required' }]}
					>
						<Input placeholder={DEFAULT_LLM_CONFIG.base_url} />
					</Form.Item>
					<Form.Item
						name="api_key"
						label="API Key"
						rules={[{ required: true, message: 'Required' }]}
					>
						<Input.Password placeholder="sk-…" />
					</Form.Item>
					<Form.Item
						name="model"
						label="Model"
						rules={[{ required: true, message: 'Required' }]}
					>
						<Input placeholder={DEFAULT_LLM_CONFIG.model} />
					</Form.Item>
					<Button type="primary" onClick={test} loading={testing}>
						Test Connection
					</Button>
				</Form>

				<Typography.Paragraph
					type="secondary"
					style={{ fontSize: 12, marginTop: 16, marginBottom: 0 }}
				>
					Changes are saved automatically. Your API key is stored only in this browser
					(localStorage) and never uploaded anywhere. Any OpenAI-compatible endpoint works
					(Base URL + Model). Once configured, "AI Deep Analysis" becomes available on each
					tool page.
				</Typography.Paragraph>
			</Card>
		</div>
	);
}
