function output = overlay_mask_rgb(image, mask, color, alpha)
%OVERLAY_MASK_RGB Blend a binary mask into an RGB image.

if nargin < 3
    color = [0.05, 0.72, 0.38];
end
if nargin < 4
    alpha = 0.42;
end

if size(image, 3) == 1
    image = repmat(image, 1, 1, 3);
end
image = im2double(image);
mask = logical(mask);
output = image;

for channel = 1:3
    plane = output(:, :, channel);
    plane(mask) = (1 - alpha) .* plane(mask) + alpha .* color(channel);
    output(:, :, channel) = plane;
end
end
