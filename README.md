# RPLBench 中文论文工程

本目录保存与当前正式数据、审计记录和研究验证证据同步的中文论文。论文覆盖 328 条 chain、四个来源数据包、328 条 release-call 执行、147 条独立 AppWorld official-solution 执行、按对象拆分的最终状态验证和人工复核边界。

## 证据来源

- 锁定源数据：通过 `--benchmarks-root` 或 `RPLBENCH_SOURCE_ROOT` 显式指定；
- 构建源码：`src/rplbench/`
- 正式数据：`release/`
- 验证与重放记录：`audit/`
- 研究验证记录：`evaluation/`
- 论文机器可读统计：`paper/evidence/`

重新生成证据：

```bash
PYTHONPATH=src python3 paper/scripts/generate_artifacts.py \
  --benchmarks-root /path/to/source_benchmarks
```

## 编译

```bash
cd paper/manuscript
xelatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
xelatex -interaction=nonstopmode -halt-on-error main.tex
xelatex -interaction=nonstopmode -halt-on-error main.tex
mkdir -p ../output/pdf
cp main.pdf ../output/pdf/rplbench_builder_cn.pdf
```

稳定 PDF 位于 `paper/output/pdf/rplbench_builder_cn.pdf`。

论文明确区分 source reference replay、环境执行、final-state verification 和真实人类复核。完成门状态见 `paper/state/completion_audit.md`。
