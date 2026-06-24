function fig15_runtime_screenshots()
%FIG15_RUNTIME_SCREENSHOTS Arrange real terminal captures for the paper.

paths = project_paths();
workspace = fileparts(paths.root);
screenshotDir = fullfile(workspace, '课程论文要求', '图片');

busi = imread(fullfile(screenshotDir, 'busi_ukan代码最终过程.png'));
cvc = imread(fullfile(screenshotDir, 'cvc_ukan代码运行最终过程-epoch100.png'));
evaluation = imread(fullfile(screenshotDir, 'mess', '生成 metrics.csv 和预测 mask.png'));

% Retain the late-epoch region where checkpoint saving and convergence are visible.
busi = busi(max(1, round(size(busi, 1) * 0.35)):end, :, :);
cvc = cvc(max(1, round(size(cvc, 1) * 0.35)):end, :, :);

fig = new_paper_figure(1900, 1200);
layout = tiledlayout(fig, 2, 2, 'TileSpacing', 'compact', 'Padding', 'compact');
layout.OuterPosition = [0.01, 0.04, 0.98, 0.90];
annotation(fig, 'textbox', [0.15, 0.945, 0.70, 0.045], ...
    'String', '真实终端运行记录：训练、评估与预测文件生成', ...
    'EdgeColor', 'none', 'HorizontalAlignment', 'center', ...
    'FontSize', 18, 'FontWeight', 'bold');

show_capture(nexttile(layout, 1), busi, ...
    'BUSI U-KAN：训练后段与 best checkpoint 保存');
show_capture(nexttile(layout, 2), cvc, ...
    'CVC-ClinicDB U-KAN：训练后段与验证指标');
show_capture(nexttile(layout, 3, [1, 2]), evaluation, ...
    '统一 evaluate.py：IoU/Dice、参数量、推理时间与预测 mask 生成');

annotation(fig, 'textbox', [0.12, 0.002, 0.76, 0.03], ...
    'String', '截图来源：作者在本地 Windows / Anaconda / PyTorch 环境实际运行项目时截取；MATLAB 仅负责裁切与排版。', ...
    'EdgeColor', 'none', 'HorizontalAlignment', 'center', ...
    'FontSize', 10, 'Color', [0.30, 0.34, 0.38]);

export_paper_figure(fig, "fig15_runtime_screenshots_matlab");
end


function show_capture(ax, imageData, panelTitle)
image(ax, imageData);
axis(ax, 'image');
axis(ax, 'off');
title(ax, panelTitle, 'FontSize', 12, 'FontWeight', 'bold');
set(ax, 'Color', [0.96, 0.97, 0.98]);
end
