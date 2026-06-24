function output = overlay_prediction_errors(image, groundTruth, prediction)
%OVERLAY_PREDICTION_ERRORS Blend TP, FP and FN regions into an image.
% Green: true positive; red: false positive; blue: false negative.

image = ensure_rgb(image);
image = im2double(image);
groundTruth = logical(groundTruth);
prediction = logical(prediction);

truePositive = groundTruth & prediction;
falsePositive = ~groundTruth & prediction;
falseNegative = groundTruth & ~prediction;

output = image;
output = blend_region(output, truePositive, [0.05, 0.78, 0.38], 0.38);
output = blend_region(output, falsePositive, [0.92, 0.12, 0.12], 0.56);
output = blend_region(output, falseNegative, [0.08, 0.38, 0.95], 0.58);
end

function output = blend_region(output, mask, color, alpha)
for channel = 1:3
    plane = output(:, :, channel);
    plane(mask) = (1 - alpha) .* plane(mask) + alpha .* color(channel);
    output(:, :, channel) = plane;
end
end
