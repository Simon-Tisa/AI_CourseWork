function [imagePath, maskPath, predictionPath] = sample_paths(dataset, sampleId, runName)
%SAMPLE_PATHS Resolve processed image, mask and optional prediction paths.

paths = project_paths();
dataset = lower(string(dataset));
sampleId = string(sampleId);

imagePath = fullfile(paths.data, dataset, 'images', sampleId + ".png");
if dataset == "busi"
    maskPath = fullfile(paths.data, dataset, 'masks', '0', sampleId + "_mask.png");
else
    maskPath = fullfile(paths.data, dataset, 'masks', '0', sampleId + ".png");
end

predictionPath = "";
if nargin >= 3 && strlength(string(runName)) > 0
    predictionPath = fullfile(paths.results, string(runName), 'predictions', sampleId + ".png");
end
end
