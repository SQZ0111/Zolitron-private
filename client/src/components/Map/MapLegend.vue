<template>
  <aside class="map-legend" aria-label="Map marker legend">
    <h2 class="legend-title">Legend</h2>
    <div class="legend-item">
      <span class="legend-color" />
      <span>Trash or litter detection</span>
    </div>
  </aside>
</template>

<style scoped>
.map-legend {
  position: absolute;
  right: 20px;
  bottom: 28px;
  z-index: 3;
  min-width: 190px;
  padding: 14px 16px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 3px 14px rgba(13, 71, 161, 0.2);
  font-size: 0.82rem;
  backdrop-filter: blur(8px);
}

.legend-title {
  margin-bottom: 9px;
  font-size: 0.9rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 9px;
  margin-top: 6px;
}

.legend-color {
  width: 14px;
  height: 14px;
  flex: 0 0 auto;
  border-radius: 50%;
  background: #990066;
}

@media (max-width: 600px) {
  .map-legend {
    right: 12px;
    bottom: 20px;
    min-width: 0;
    padding: 10px 12px;
    font-size: 0.72rem;
  }
}
</style>
