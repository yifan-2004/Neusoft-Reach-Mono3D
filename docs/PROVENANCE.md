# 来源与改动范围

项目展示名称：Neusoft Reach Mono3D。公司名称的使用和公开由项目发布者确认已获授权。

## 第三方算法

- 上游：https://github.com/alanzhangcs/MonoCoP
- 基准提交：`7d3932444f7ea94be564ae61a0b334fc6673213b`
- 论文：https://arxiv.org/abs/2503.11651
- 作者：Zhihao Zhang、Abhinav Kumar、Girish Chandar Ganesan、Xiaoming Liu。
- LICENSE 中完整保留上游 MIT 版权与许可。嵌套依赖的许可也保留在原目录。
- 保留 Git 历史和模型内部名称，不把上游贡献改记到新作者名下。

## 本版本新增

- 中文入门 README、明确注明来源的官方结果表。
- 标准库实现的 KITTI 预测投影、相机视图与鸟瞰图报告。
- 不依赖权重的人工几何示例与工具验证。
- 根据原作者描述重绘的概念流程图，不是新的网络结构。

未下载模型权重或 KITTI 数据集；未执行模型训练、推理和精度复测。官方检测图片与指标属于上游成果，新增人工示例不能作为模型评测结果。
