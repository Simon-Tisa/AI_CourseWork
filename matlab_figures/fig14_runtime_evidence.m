function fig14_runtime_evidence()
%FIG14_RUNTIME_EVIDENCE Create a reproducibility evidence board.

paths = project_paths();
results = readtable(fullfile(paths.tables, 'segmentation_results.csv'), ...
    'TextType', 'string');
busi = results(results.name == "busi_ukan_seed2981", :);
cvc = results(results.name == "cvc_ukan_seed2981", :);

fig = new_paper_figure(1900, 1050);
ax = axes(fig, 'Position', [0.02, 0.03, 0.96, 0.92]);
axis(ax, [0, 1, 0, 1]);
axis(ax, 'off');
title(ax, '从运行命令到论文结果的可复现证据链', ...
    'FontSize', 19, 'FontWeight', 'bold');

columnX = [0.03, 0.25, 0.68];
columnW = [0.18, 0.39, 0.29];
headers = ["阶段", "实际命令或配置入口", "可核验产物与结果"];
for column = 1:3
    rectangle(ax, 'Position', [columnX(column), 0.84, columnW(column), 0.08], ...
        'FaceColor', [0.12, 0.30, 0.48], 'EdgeColor', 'none');
    text(ax, columnX(column) + columnW(column) / 2, 0.88, headers(column), ...
        'HorizontalAlignment', 'center', 'VerticalAlignment', 'middle', ...
        'Color', 'white', 'FontWeight', 'bold', 'FontSize', 12);
end

stages = [
    "环境诊断"
    "模型训练"
    "统一评估"
    "结果汇总"
];
commands = [
    "run_python.ps1 scripts/doctor_env.py"
    "run_python.ps1 scripts/train.py --config configs/busi_ukan.yaml"
    "run_python.ps1 scripts/evaluate.py --name busi_ukan_seed2981"
    "run_python.ps1 scripts/summarize_results.py"
];
evidence = [
    sprintf("Python 3.10.18 | PyTorch 2.9.1+cu126\nCUDA 12.6 | RTX 4080 Laptop GPU")
    sprintf("config.yml | log.csv | model.pth\n100 epoch，best checkpoint 按 val IoU 保存")
    sprintf("BUSI U-KAN: IoU %.4f, Dice %.4f\nCVC U-KAN: IoU %.4f, Dice %.4f", ...
        busi.iou, busi.dice, cvc.iou, cvc.dice)
    sprintf("paper/tables/segmentation_results.csv\n训练曲线、预测 mask、MATLAB 图表与论文表格")
];

rowY = [0.65, 0.47, 0.29, 0.11];
fills = [
    0.91, 0.96, 0.99
    0.94, 0.98, 0.94
    1.00, 0.97, 0.90
    0.97, 0.94, 0.99
];
for row = 1:4
    for column = 1:3
        rectangle(ax, 'Position', [columnX(column), rowY(row), columnW(column), 0.14], ...
            'FaceColor', fills(row, :), 'EdgeColor', [0.75, 0.79, 0.83], ...
            'LineWidth', 0.9);
    end
    text(ax, columnX(1) + columnW(1) / 2, rowY(row) + 0.07, stages(row), ...
        'HorizontalAlignment', 'center', 'VerticalAlignment', 'middle', ...
        'FontWeight', 'bold', 'FontSize', 12);
    text(ax, columnX(2) + 0.012, rowY(row) + 0.07, commands(row), ...
        'HorizontalAlignment', 'left', 'VerticalAlignment', 'middle', ...
        'FontName', 'Consolas', 'FontSize', 10, 'Interpreter', 'none');
    text(ax, columnX(3) + 0.012, rowY(row) + 0.07, evidence(row), ...
        'HorizontalAlignment', 'left', 'VerticalAlignment', 'middle', ...
        'FontSize', 10, 'Interpreter', 'none');
end

annotation(fig, 'textbox', [0.18, 0.005, 0.64, 0.035], ...
    'String', '所有数字均可由实验目录中的配置、日志、checkpoint、metrics.csv 和预测文件反向追溯。', ...
    'EdgeColor', 'none', 'HorizontalAlignment', 'center', ...
    'FontSize', 10, 'Color', [0.30, 0.34, 0.38]);

export_paper_figure(fig, "fig14_runtime_evidence_matlab");
end
