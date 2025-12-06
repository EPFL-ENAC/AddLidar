/** Pointcloud metadata types based on Potree 2.0 format */

export type AttributeType =
  | "int8"
  | "uint8"
  | "int16"
  | "uint16"
  | "int32"
  | "uint32"
  | "int64"
  | "uint64"
  | "float"
  | "double";

export interface PointcloudAttribute {
  name: string;
  description: string;
  size: number;
  numElements: number;
  elementSize: number;
  type: AttributeType;
  min: number[];
  max: number[];
  scale: number[];
  offset: number[];
  histogram?: number[];
}

export interface BoundingBox {
  min: [number, number, number];
  max: [number, number, number];
}

export interface HierarchyInfo {
  firstChunkSize: number;
  stepSize: number;
  depth: number;
}

export interface PointcloudMetadata {
  version: string;
  name: string;
  description: string;
  points: number;
  projection: string;
  hierarchy: HierarchyInfo;
  offset: [number, number, number];
  scale: [number, number, number];
  spacing: number;
  boundingBox: BoundingBox;
  encoding: string;
  attributes: PointcloudAttribute[];
}

/** Common attribute names found in LiDAR point clouds */
export type CommonAttributeName =
  | "position"
  | "intensity"
  | "return number"
  | "number of returns"
  | "classification"
  | "scan angle rank"
  | "user data"
  | "point source id"
  | "gps-time"
  | "rgb"
  | "rgba"
  | "normal x"
  | "normal y"
  | "normal z";

/** Helper to find an attribute by name (case-insensitive partial match) */
export function findAttribute(
  metadata: PointcloudMetadata | null,
  namePattern: string,
): PointcloudAttribute | undefined {
  if (!metadata?.attributes) return undefined;
  const pattern = namePattern.toLowerCase();
  return metadata.attributes.find((attr) =>
    attr.name.toLowerCase().includes(pattern),
  );
}

/** Get point source ID range from metadata */
export function getPointSourceIdRange(
  metadata: PointcloudMetadata | null,
): { min: number; max: number } | null {
  const attr = findAttribute(metadata, "point source");
  if (!attr?.min?.[0] || !attr?.max?.[0]) return null;
  return { min: attr.min[0], max: attr.max[0] };
}

/** Get classification histogram if available */
export function getClassificationHistogram(
  metadata: PointcloudMetadata | null,
): number[] | null {
  const attr = findAttribute(metadata, "classification");
  return attr?.histogram ?? null;
}
