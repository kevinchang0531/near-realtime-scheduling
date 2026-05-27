# near-realtime-scheduling

近即時排程系統（Near Real-Time Scheduling）。

## 專案概覽

Python-based 排程系統，目標是近即時（near real-time）任務調度與執行。

## 目錄結構

```
near-realtime-scheduling/
├── src/           # 核心程式碼
├── tests/         # 單元測試與整合測試
├── docs/          # 文件
├── data/          # 資料檔案
├── CLAUDE.md      # 本檔案
└── README.md
```

## 開發規範

- Python 3.11+
- 測試框架：pytest
- 程式碼格式：black + ruff
- 型別標註：盡量使用 type hints

## 常用指令

```bash
# 執行測試
pytest tests/

# 格式化
black src/ tests/
ruff check src/ tests/
```
