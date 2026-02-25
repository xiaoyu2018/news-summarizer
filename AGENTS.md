# News Summarizer Project

AI 新闻摘要生成器。从指定信息源收集行业新闻，AI 生成摘要并定时发送。

## Project Structure

```
news-summarizer/
├── conf/                      # 配置文件目录
│   ├── config.yaml            # 配置文件（不提交）
│   └── config.example.yaml    # 配置示例
├── prompts/                   # 提示词目录
├── src/                      # 源代码
│   ├── main.py               # 主入口
│   ├── models.py             # 数据模型
│   ├── config_loader.py      # 配置加载器
│   ├── collectors/          # 收集器
│   │   ├── base.py         # Collector 基类
│   │   └── email_collector.py
│   ├── processors/          # 处理器
│   │   ├── base.py
│   │   └── ai_processor.py
│   ├── senders/             # 发送器
│   │   ├── base.py
│   │   └── email_sender.py
│   └── utils/               # 工具类
│       ├── logger.py
│       └── html_cleaner.py
├── tests/                   # 测试目录
│   └── test_collector.py
├── pyproject.toml
└── README.md
```

## Commands

- `uv sync` - 安装依赖
- `python -m pytest tests/` - 运行测试
- `uv run src/main.py` - 运行主程序

## coding rules

### 在代码中使用异常处理要求：
- 总体要求：
异常：应对“意外”情况（你无法控制的外部因素或程序本身错误）
if-else：处理“预期”情况（你已知的可能状态并可以主动检查）
两者结合使用：用 if 预防可预见的错误，用异常处理不可控的异常情况。
- 适用场景（此类场景才能使用异常处理）：
1. 处理不可预测的、非常规的错误，如：
外部资源失败（文件缺失、网络超时、数据库连接断开）
调用第三方库/API 抛出的异常
程序内部状态不一致（例如本应存在的对象为 None）
2. 在多层调用间传递错误，避免每层都检查返回值
3. 发生无法继续执行的错误时，向上层报告或终止程序
- 使用要求（决定使用异常处理时的原则）：
1. 捕获特定异常，避免 except: 或 except Exception（除非立即记录并重新抛出）
2. 仅在能真正处理异常的地方捕获，否则让异常继续传播
3. 缩小 try 块范围，只包裹可能抛出异常的代码
4. 用 finally 或 with 确保资源释放
5. 记录异常日志（logging）以便排查
6. 不要用异常控制正常流程（如循环终止）
