function plot_training_dataset(dataset, outputBaseName)
%PLOT_TRAINING_DATASET Plot loss, validation IoU and validation Dice.

paths = project_paths();
dataset = lower(string(dataset));
if dataset == "busi"
    runNames = ["busi_unet_seed2981", "busi_no_kan_seed2981", ...
        "busi_ukan_seed2981", "busi_attention_ukan_seed2981"];
    datasetLabel = "BUSI";
else
    runNames = ["cvc_unet_seed2981", "cvc_no_kan_seed2981", ...
        "cvc_ukan_seed2981", "cvc_attention_ukan_seed2981"];
    datasetLabel = "CVC-ClinicDB";
end

modelLabels = ["U-Net", "U-KAN(no-KAN)", "U-KAN", "Attention-U-KAN"];
colors = lines(4);
logs = cell(1, 4);
for index = 1:4
    logs{index} = readtable(fullfile(paths.results, runNames(index), 'log.csv'));
end

fig = new_result_figure(1800, 620);
layout = tiledlayout(fig, 1, 3, 'TileSpacing', 'compact', 'Padding', 'compact');
sgtitle(layout, datasetLabel + " 四模型训练过程", ...
    'FontSize', 18, 'FontWeight', 'bold');

metricNames = ["loss", "val_iou", "val_dice"];
panelTitles = ["训练损失", "验证集 IoU", "验证集 Dice"];
for panelIndex = 1:3
    ax = nexttile;
    hold(ax, 'on');
    for modelIndex = 1:4
        logTable = logs{modelIndex};
        epochs = logTable.epoch + 1;
        values = logTable.(metricNames(panelIndex));
        plot(ax, epochs, values, 'LineWidth', 1.45, ...
            'Color', colors(modelIndex, :), ...
            'DisplayName', modelLabels(modelIndex));
        if panelIndex > 1
            [bestValue, bestIndex] = max(values);
            plot(ax, epochs(bestIndex), bestValue, 'o', ...
                'MarkerSize', 5, ...
                'MarkerFaceColor', colors(modelIndex, :), ...
                'MarkerEdgeColor', 'white', ...
                'HandleVisibility', 'off');
        end
    end
    hold(ax, 'off');
    grid(ax, 'on');
    ax.GridAlpha = 0.15;
    xlim(ax, [1, 100]);
    xlabel(ax, 'Epoch');
    title(ax, panelTitles(panelIndex));
    if panelIndex == 1
        ylabel(ax, 'Loss');
    else
        ylabel(ax, 'Score');
    end
end
legend(ax, modelLabels, 'Orientation', 'horizontal', 'Location', 'southoutside');

export_result_figure(fig, outputBaseName);
end
