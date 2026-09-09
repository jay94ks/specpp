"""examples/doom/automap.md 의 # Domain/# Behavior 참조 구현."""

MIN_ZOOM = 0.25
MAX_ZOOM = 4.0


class AutoMap:
    def __init__(self):
        self.isOpen = False
        self.centerX = 0.0
        self.centerY = 0.0
        self.zoom = 1.0
        self.revealedLines = []

    # spp-source: examples/doom/automap.md#Feature:_자동_지도_토글
    def toggle(self):
        self.isOpen = not self.isOpen

    # spp-source: examples/doom/automap.md#Feature:_지도에_선_드러내기
    def revealFromSubsector(self, subsector):
        for seg in subsector.segs:
            line = seg.lineDef
            if line.isSecret:
                continue
            if line not in self.revealedLines:
                self.revealedLines.append(line)

    # spp-source: examples/doom/automap.md#Feature:_지도_이동·확대
    def pan_and_zoom(self, panX, panY, zoomDelta):
        self.centerX += panX
        self.centerY += panY
        self.zoom = max(MIN_ZOOM, min(MAX_ZOOM, self.zoom + zoomDelta))
