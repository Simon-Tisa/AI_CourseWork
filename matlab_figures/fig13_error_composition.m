function fig13_error_composition()
%FIG13_ERROR_COMPOSITION Analyze false-positive and false-negative balance.

paths = project_paths();
modelLabels = ["U-KAN", "Attention-U-KAN"];
busiRuns = ["busi_ukan_seed2981", "busi_attention_ukan_seed2981"];
cvcRuns = ["cvc_ukan_seed2981", "cvc_attention_ukan_seed2981"];
busi = collect_per_image_metrics("busi", busiRuns, modelLabels);
cvc = collect_per_image_metrics("cvc", cvcRuns, modelLabels);

groupLabels = ["BUSI U-KAN", "BUSI Attention", "CVC U-KAN", "CVC Attention"];
globalValues = [
    global_error_ratios(busi, modelLabels(1))
    global_error_ratios(busi, modelLabels(2))
    global_error_ratios(cvc, modelLabels(1))
    global_error_ratios(cvc, modelLabels(2))
];

fig = new_paper_figure(1700, 680);
layout = tiledlayout(fig, 1, 2, 'TileSpacing', 'compact', 'Padding', 'compact');
sgtitle(layout, '失败分析：过分割与漏分割误差构成', ...
    'FontSize', 18, 'FontWeight', 'bold');

ax1 = nexttile;
bars = bar(ax1, globalValues, 'grouped');
bars(1).FaceColor = [0.86, 0.18, 0.18];
bars(2).FaceColor = [0.12, 0.38, 0.88];
bars(1).EdgeColor = 'none';
bars(2).EdgeColor = 'none';
grid(ax1, 'on');
ax1.GridAlpha = 0.15;
ylabel(ax1, '误差像素 / 真值前景像素');
title(ax1, '全验证集误差比例');
xticks(ax1, 1:4);
xticklabels(ax1, groupLabels);
xtickangle(ax1, 18);
legend(ax1, {'FP：过分割', 'FN：漏分割'}, ...
    'Location', 'southoutside', 'Orientation', 'horizontal');

ax2 = nexttile;
hold(ax2, 'on');
scatter(ax2, busi.fp_ratio(busi.model == modelLabels(1)), ...
    busi.fn_ratio(busi.model == modelLabels(1)), ...
    26, [0.18, 0.48, 0.78], 'filled', 'MarkerFaceAlpha', 0.45);
scatter(ax2, cvc.fp_ratio(cvc.model == modelLabels(1)), ...
    cvc.fn_ratio(cvc.model == modelLabels(1)), ...
    26, [0.94, 0.52, 0.12], 'filled', 'MarkerFaceAlpha', 0.45);
limit = min(3, max([xlim(ax2), ylim(ax2)]));
plot(ax2, [0, limit], [0, limit], '--', 'Color', [0.3, 0.3, 0.3], ...
    'LineWidth', 1.2);
hold(ax2, 'off');
xlim(ax2, [0, limit]);
ylim(ax2, [0, limit]);
axis(ax2, 'square');
grid(ax2, 'on');
ax2.GridAlpha = 0.15;
xlabel(ax2, '逐图 FP / 真值面积');
ylabel(ax2, '逐图 FN / 真值面积');
title(ax2, 'U-KAN 逐图误差平衡');
legend(ax2, {'BUSI', 'CVC-ClinicDB', 'FP=FN'}, 'Location', 'northeast');

errorTable = table(groupLabels', globalValues(:, 1), globalValues(:, 2), ...
    'VariableNames', {'group', 'fp_over_gt', 'fn_over_gt'});
writetable(errorTable, fullfile(paths.output, 'fig13_global_error_composition.csv'));

export_paper_figure(fig, "fig13_error_composition_matlab");
end

function ratios = global_error_ratios(metrics, modelLabel)
selected = metrics.model == modelLabel;
fp = sum(metrics.fp_ratio(selected) .* metrics.mask_ratio(selected));
fn = sum(metrics.fn_ratio(selected) .* metrics.mask_ratio(selected));
gt = sum(metrics.mask_ratio(selected));
ratios = [fp / gt, fn / gt];
end
