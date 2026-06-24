function fig12_failure_distribution_size()
%FIG12_FAILURE_DISTRIBUTION_SIZE Analyze per-image Dice and lesion size.

paths = project_paths();
modelLabels = ["U-Net", "U-KAN(no-KAN)", "U-KAN", "Attention-U-KAN"];
busiRuns = ["busi_unet_seed2981", "busi_no_kan_seed2981", ...
    "busi_ukan_seed2981", "busi_attention_ukan_seed2981"];
cvcRuns = ["cvc_unet_seed2981", "cvc_no_kan_seed2981", ...
    "cvc_ukan_seed2981", "cvc_attention_ukan_seed2981"];

busi = collect_per_image_metrics("busi", busiRuns, modelLabels);
cvc = collect_per_image_metrics("cvc", cvcRuns, modelLabels);
writetable(busi, fullfile(paths.output, 'busi_per_image_metrics.csv'));
writetable(cvc, fullfile(paths.output, 'cvc_per_image_metrics.csv'));

fig = new_paper_figure(1800, 1200);
layout = tiledlayout(fig, 2, 2, 'TileSpacing', 'compact', 'Padding', 'compact');
sgtitle(layout, '失败分析：逐图性能分布与病灶面积分层', ...
    'FontSize', 18, 'FontWeight', 'bold');

plot_box_panel(nexttile, busi, modelLabels, 'BUSI：逐图 Dice 分布');
plot_box_panel(nexttile, cvc, modelLabels, 'CVC-ClinicDB：逐图 Dice 分布');
plot_size_panel(nexttile, busi, modelLabels, 'BUSI：不同病灶面积的平均 Dice');
plot_size_panel(nexttile, cvc, modelLabels, 'CVC-ClinicDB：不同病灶面积的平均 Dice');

export_paper_figure(fig, "fig12_failure_distribution_size_matlab");
end

function plot_box_panel(ax, metrics, modelLabels, panelTitle)
groups = categorical(metrics.model, modelLabels, 'Ordinal', true);
boxchart(ax, groups, metrics.dice, ...
    'BoxFaceColor', [0.20, 0.48, 0.76], ...
    'MarkerStyle', '.', ...
    'JitterOutliers', 'on');
grid(ax, 'on');
ax.GridAlpha = 0.13;
ylim(ax, [0, 1.02]);
ylabel(ax, '逐图 Dice');
title(ax, panelTitle);
xtickangle(ax, 15);
end

function plot_size_panel(ax, metrics, modelLabels, panelTitle)
sampleRows = metrics.model == modelLabels(1);
sampleRatios = metrics.mask_ratio(sampleRows);
edges = quantile(sampleRatios, [0, 1/3, 2/3, 1]);
edges(1) = -inf;
edges(end) = inf;
binLabels = ["小病灶", "中等病灶", "大病灶"];
values = zeros(numel(modelLabels), 3);

for modelIndex = 1:numel(modelLabels)
    modelRows = metrics.model == modelLabels(modelIndex);
    for binIndex = 1:3
        selected = modelRows ...
            & metrics.mask_ratio > edges(binIndex) ...
            & metrics.mask_ratio <= edges(binIndex + 1);
        values(modelIndex, binIndex) = mean(metrics.dice(selected));
    end
end

bars = bar(ax, values, 'grouped');
colors = [0.18, 0.45, 0.76; 0.95, 0.55, 0.14; 0.18, 0.65, 0.42];
for index = 1:3
    bars(index).FaceColor = colors(index, :);
    bars(index).EdgeColor = 'none';
end
grid(ax, 'on');
ax.GridAlpha = 0.13;
ylim(ax, [0.45, 0.95]);
ylabel(ax, '平均逐图 Dice');
title(ax, panelTitle);
xticks(ax, 1:numel(modelLabels));
xticklabels(ax, modelLabels);
xtickangle(ax, 15);
legend(ax, binLabels, 'Location', 'southoutside', 'Orientation', 'horizontal');
end
