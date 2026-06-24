function output = prediction_error_rgb(groundTruth, prediction)
%PREDICTION_ERROR_RGB Encode TP, FP and FN pixels with fixed colors.
% Green: true positive; red: false positive; blue: false negative.

groundTruth = logical(groundTruth);
prediction = logical(prediction);
output = zeros([size(groundTruth), 3], 'uint8');

truePositive = groundTruth & prediction;
falsePositive = ~groundTruth & prediction;
falseNegative = groundTruth & ~prediction;

output(:, :, 1) = uint8(falsePositive) .* 235;
output(:, :, 2) = uint8(truePositive) .* 190;
output(:, :, 3) = uint8(falseNegative) .* 235;
end
