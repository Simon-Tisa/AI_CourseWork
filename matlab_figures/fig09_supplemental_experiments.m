function fig09_supplemental_experiments()
%FIG09_SUPPLEMENTAL_EXPERIMENTS Plot seed stability and continued training.

paths = project_paths();
seedData = readtable(fullfile(paths.tables, 'busi_seed_stability.csv'), ...
    'TextType', 'string');
continueData = readtable(fullfile(paths.tables, 'cvc_continued_training.csv'), ...
    'TextType', 'string');

fig = new_result_figure(1800, 650);
layout = tiledlayout(fig, 1, 3, 'TileSpacing', 'compact', 'Padding', 'compact');
sgtitle(layout, '补充实验：随机种子稳定性与继续训练诊断', ...
    'FontSize', 18, 'FontWeight', 'bold');

modelLabels = ["U-KAN(no-KAN)", "U-KAN"];
seedLabels = ["seed2981", "seed6142", "两 seed 均值"];
colors = [0.17, 0.47, 0.77; 0.94, 0.52, 0.12; 0.18, 0.64, 0.42];

iouValues = [seedData.seed2981_iou, seedData.seed6142_iou, seedData.mean_iou];
diceValues = [seedData.seed2981_dice, seedData.seed6142_dice, seedData.mean_dice];

ax1 = nexttile;
bars = bar(ax1, iouValues, 'grouped');
style_bars(bars, colors);
format_grouped_panel(ax1, modelLabels, [0.55, 0.71], 'IoU', 'BUSI：IoU 稳定性');
add_bar_labels(ax1, bars, 4);
legend(ax1, seedLabels, 'Location', 'southoutside', 'Orientation', 'horizontal');

ax2 = nexttile;
bars = bar(ax2, diceValues, 'grouped');
style_bars(bars, colors);
format_grouped_panel(ax2, modelLabels, [0.70, 0.84], 'Dice', 'BUSI：Dice 稳定性');
add_bar_labels(ax2, bars, 4);
legend(ax2, seedLabels, 'Location', 'southoutside', 'Orientation', 'horizontal');

ax3 = nexttile;
cvcValues = [continueData.iou, continueData.dice];
bars = bar(ax3, cvcValues, 'grouped');
bars(1).FaceColor = [0.15, 0.43, 0.78];
bars(2).FaceColor = [0.95, 0.55, 0.15];
bars(1).EdgeColor = 'none';
bars(2).EdgeColor = 'none';
grid(ax3, 'on');
ax3.GridAlpha = 0.15;
ylim(ax3, [0.75, 0.90]);
ylabel(ax3, '指标值');
title(ax3, 'CVC：从最佳 checkpoint 继续训练');
xticks(ax3, 1:2);
xticklabels(ax3, ["原始 100 epoch", "继续训练 50 epoch"]);
xtickangle(ax3, 12);
legend(ax3, {'IoU', 'Dice'}, 'Location', 'southoutside', 'Orientation', 'horizontal');
add_bar_labels(ax3, bars, 4);

export_result_figure(fig, "fig09_supplemental_experiments_matlab");
end

function style_bars(bars, colors)
for index = 1:numel(bars)
    bars(index).FaceColor = colors(index, :);
    bars(index).EdgeColor = 'none';
end
end

function format_grouped_panel(ax, labels, limits, yLabel, panelTitle)
grid(ax, 'on');
ax.GridAlpha = 0.15;
ylim(ax, limits);
ylabel(ax, yLabel);
title(ax, panelTitle);
xticks(ax, 1:numel(labels));
xticklabels(ax, labels);
xtickangle(ax, 12);
end

function add_bar_labels(ax, bars, digits)
offset = 0.006 * range(ylim(ax));
for index = 1:numel(bars)
    labels = compose("%." + digits + "f", bars(index).YData);
    text(ax, bars(index).XEndPoints, bars(index).YEndPoints + offset, labels, ...
        'HorizontalAlignment', 'center', 'FontSize', 8);
end
end
