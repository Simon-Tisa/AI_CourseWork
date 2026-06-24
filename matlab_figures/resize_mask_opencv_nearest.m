function resized = resize_mask_opencv_nearest(mask, targetSize)
%RESIZE_MASK_OPENCV_NEAREST Match cv2.INTER_NEAREST index mapping.
%
% OpenCV maps destination index d to floor(d * source_size / target_size).
% MATLAB imresize uses a different pixel-center convention, which can move
% boundary pixels and slightly change global IoU/Dice.

sourceHeight = size(mask, 1);
sourceWidth = size(mask, 2);
targetHeight = targetSize(1);
targetWidth = targetSize(2);

rowIndices = floor((0:(targetHeight - 1)) .* sourceHeight ./ targetHeight) + 1;
columnIndices = floor((0:(targetWidth - 1)) .* sourceWidth ./ targetWidth) + 1;
rowIndices = min(max(rowIndices, 1), sourceHeight);
columnIndices = min(max(columnIndices, 1), sourceWidth);

resized = mask(rowIndices, columnIndices);
end
