# CEO Operating System（创始人操作系统）

**Agent Skill + 可运行 Python 工具**：SaaS 健康分、股权稀释、路演评分 + 融资/PMF 框架。

---

## 安装（Cursor Agent Skill）

```bash
git clone https://github.com/kimogrant/ceo-operating-system.git
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
