from skimage import data, io, filter, transform

from base import Component, InputPort, OutputPort


class EdgeDetector(Component):
    image = InputPort("Input image")
    detected_edges = OutputPort("Detected edges")

    def process(self):
        super(EdgeDetector, self).process()
        self.detected_edges.value = filter.sobel(self.image.value)

class Resize(Component):
    original_image = InputPort("Original image")
    resized_image = OutputPort("Resized image")

    def process(self):
        super(Resize, self).process()
        self.resized_image.value = transform.pyramid_reduce(self.original_image.value, downscale=2)

if __name__ == '__main__':
    edge_detector = EdgeDetector('ed1')
    resize = Resize('rsz1')
    resize_bis = Resize('rsz2')

    # Connecting resize to resize_bis, and resize_bis to the edge detector
    resize.resized_image.connect(resize_bis.original_image)
    resize_bis.resized_image.connect(edge_detector.image)

    # Manually filling the first block's input port buffer with a coins image
    resize.original_image.value = data.coins()

    # Processing all blocks, from the first one
    resize.process_all()

    # Viewing the result
    io.imshow(edge_detector.detected_edges.value)