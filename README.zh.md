# CEO Operating System（创始人操作系统）

**Agent Skill + 可运行 Python 工具**：SaaS 健康分、股权稀释、路演评分 + 融资/PMF 框架。

---

## 安装（Cursor Agent Skill）

```bash
git clone https://github.com/kioiskio/ceo-operating-system.git
cd ceo-operating-system
chmod +x skill.sh
./skill.sh install /path/to/your/project
```

路径：`.cursor/skills/ceo-operating-system/`（含 `tools/`、`references/`）

调用：**`/ceo-operating-system`**

---

## 工具（本地也可直接跑）

```bash
python tools/saas-metrics/saas_health.py -e      # SaaS 指标 RAG + 总分
python tools/equity-calculator/equity_calc.py -e # 多轮稀释 cap table
python tools/pitch-deck-scorer/scorer.py -e      # 路演 checklist 评分
```

---

## Web 应用

完整的 Web 界面在 [`web/`](web/README.md)（FastAPI + React + Ant Design）：三个工具的可视化操作、用户自配置 LLM 分析（OpenAI 兼容接口）、运行历史、亮/暗主题。

```bash
cd web/frontend && npm install && npm run build
cd ../backend && pip install -r requirements.txt
python -m app.main    # → http://localhost:8000
```

详见 [web/README.md](web/README.md)。

---

## Agent 硬规则

- 有数字 → **跑脚本**，禁止心算稀释或健康分  
- 融资/PMF → 读 `references/fundraising.md` / `references/pmf.md`  
- 详见 `references/tool-invocation.md`

---

## 测试

```bash
python -m unittest tests/test_tools.py -v
```

---

## 免责声明

决策辅助，非法律/税务/投资建议。

MIT · v1.1.0
