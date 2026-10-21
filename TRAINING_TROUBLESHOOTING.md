# Qwen 多模态训练告警排查

## 告警现象

训练中出现：

```text
WARNING:data_processing_qwen:[Dataset] Skip sample ... due to error: Mismatch in image token count between text and input_ids. Got ids=[2044] and text=[4240]. Likely due to truncation='max_length'. Please disable truncation or increase max_length.
```

## 根因

该告警通常表示：

- 文本中的图像占位符（例如 `<image>`）在 **tokenize 前后数量不一致**；
- 或者样本被 `truncation='max_length'` 截断后，`input_ids` 里图像 token 被截断，而原始文本中的图像标记仍然存在；
- 最终触发数据处理阶段的数量校验，样本被跳过。

## 推荐修复（按优先级）

1. **优先关闭截断**（训练时）
   - 将 tokenizer 调用中的 `truncation=False`（或不传 `truncation`）；
   - 结合动态 padding（`padding='longest'`）和合理 batch size 控制显存。

2. **必须截断时，增大 `max_length`**
   - 先统计训练集样本长度分布（P95 / P99）；
   - 将 `max_length` 提升到能覆盖包含图像占位符的长样本。

3. **截断前做一致性检查**
   - 在进入模型前，校验：`count_image_tokens(text) == count_image_tokens(input_ids)`；
   - 不一致则提前过滤并记录样本 ID，便于回查脏数据。

4. **统一模板和特殊 token 配置**
   - 确保训练模板、processor、tokenizer 使用同一套 image token 约定；
   - 避免混用不同版本 prompt 模板导致占位符不匹配。

## 快速检查清单

- [ ] 数据预处理是否启用了 `truncation='max_length'`
- [ ] `max_length` 是否明显小于多图样本所需长度
- [ ] tokenizer / processor / chat template 版本是否一致
- [ ] 被跳过样本是否集中在长文本或多图样本

## 备注

如果你已经看到日志中明确提示 `Likely due to truncation='max_length'`，基本可以先从“关闭截断”或“增大 `max_length`”两条路径开始排查。
