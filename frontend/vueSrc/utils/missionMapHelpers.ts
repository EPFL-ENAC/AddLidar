import maplibregl from "maplibre-gl";

// Tune this to make footprints stay polygons longer (lower) or switch to markers earlier (higher).
// It's the on-screen pixel size below which a footprint is "too small to read" and becomes a marker.
export const MIN_FOOTPRINT_PIXELS = 24;

export const MAX_ZOOM = 22;

export function extendBoundsFromGeometry(
  bounds: maplibregl.LngLatBounds,
  geometry: { type: string; coordinates: any },
): void {
  if (geometry.type === "Polygon") {
    (geometry.coordinates as number[][][])[0].forEach((coord) => {
      if (coord.length >= 2) bounds.extend([coord[0], coord[1]]);
    });
  } else if (geometry.type === "MultiPolygon") {
    (geometry.coordinates as number[][][][]).forEach((polygon) => {
      polygon[0].forEach((coord) => {
        if (coord.length >= 2) bounds.extend([coord[0], coord[1]]);
      });
    });
  }
}

// Lowest zoom at which the footprint diagonal occupies at least MIN_FOOTPRINT_PIXELS.
// At zoom < markerMaxZoom we render the footprint as a marker; at zoom >= markerMaxZoom as a polygon.
export function computeMarkerMaxZoom(bounds: maplibregl.LngLatBounds): number {
  if (bounds.isEmpty()) return 0;
  const sw = bounds.getSouthWest();
  const ne = bounds.getNorthEast();
  const midLat = (sw.lat + ne.lat) / 2;
  const cosLat = Math.cos((midLat * Math.PI) / 180);
  const dLatM = (ne.lat - sw.lat) * 111320;
  const dLngM = (ne.lng - sw.lng) * 111320 * cosLat;
  const diagM = Math.hypot(dLatM, dLngM);
  if (diagM <= 0) return MAX_ZOOM;
  // Web Mercator pixel resolution at zoom z, latitude φ: 156543.03 * cos(φ) / 2^z (m/px)
  const z = Math.log2((MIN_FOOTPRINT_PIXELS * 156543.03 * cosLat) / diagM);
  return Math.max(0, Math.min(MAX_ZOOM, Math.ceil(z)));
}

export function generateColorFromKey(key: string): string {
  let hash = 0;
  for (let i = 0; i < key.length; i++) {
    hash = key.charCodeAt(i) + ((hash << 5) - hash);
  }
  const hue = Math.abs(hash % 360);
  return `hsl(${hue}, 70%, 50%)`;
}

export function varyColorForLine(baseColor: string, lineIndex: number): string {
  const hueMatch = baseColor.match(/hsl\((\d+),/);
  if (!hueMatch) return baseColor;
  const baseHue = parseInt(hueMatch[1]);
  const hueShift = ((lineIndex * 8) % 40) - 20;
  const newHue = (baseHue + hueShift + 360) % 360;
  const lightness = 50 + ((lineIndex % 5) * 3 - 6);
  return `hsl(${newHue}, 70%, ${lightness}%)`;
}
