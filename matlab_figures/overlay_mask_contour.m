function output = overlay_mask_contour(image, mask, color, lineWidth)
%OVERLAY_MASK_CONTOUR Draw a binary mask boundary over an RGB image.

if nargin < 3
    color = [0.05, 0.88, 0.38];
end
if nargin < 4
    lineWidth = 2;
end

image = ensure_rgb(image);
output = im2double(image);
boundary = bwperim(logical(mask), 8);
if lineWidth > 1
    boundary = imdilate(boundary, strel('disk', lineWidth - 1, 0));
end
for channel = 1:3
    plane = output(:, :, channel);
    plane(boundary) = color(channel);
    output(:, :, channel) = plane;
end
end
