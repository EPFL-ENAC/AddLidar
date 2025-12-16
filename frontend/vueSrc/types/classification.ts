/** LAS Classification codes (LAS 1.1 - 1.4) */
export interface ClassificationCode {
  value: number;
  label: string;
  description: string;
  color?: string;
}

/** Standard LAS classification codes defined by ASPRS */
export const LAS_CLASSIFICATIONS: ClassificationCode[] = [
  {
    value: 0,
    label: "Never classified",
    description: "Never classified",
    color: "#808080",
  },
  {
    value: 1,
    label: "Unassigned",
    description: "Unassigned",
    color: "#A9A9A9",
  },
  { value: 2, label: "Ground", description: "Ground", color: "#8B4513" },
  {
    value: 3,
    label: "Low Vegetation",
    description: "Low Vegetation",
    color: "#90EE90",
  },
  {
    value: 4,
    label: "Medium Vegetation",
    description: "Medium Vegetation",
    color: "#32CD32",
  },
  {
    value: 5,
    label: "High Vegetation",
    description: "High Vegetation",
    color: "#228B22",
  },
  { value: 6, label: "Building", description: "Building", color: "#FF4500" },
  { value: 7, label: "Low Point", description: "Low Point", color: "#4B0082" },
  { value: 8, label: "Reserved", description: "Reserved", color: "#696969" },
  { value: 9, label: "Water", description: "Water", color: "#1E90FF" },
  { value: 10, label: "Rail", description: "Rail", color: "#2F4F4F" },
  {
    value: 11,
    label: "Road Surface",
    description: "Road Surface",
    color: "#696969",
  },
  { value: 12, label: "Reserved", description: "Reserved", color: "#696969" },
  {
    value: 13,
    label: "Wire - Guard (Shield)",
    description: "Wire - Guard (Shield)",
    color: "#FFD700",
  },
  {
    value: 14,
    label: "Wire - Conductor (Phase)",
    description: "Wire - Conductor (Phase)",
    color: "#FFA500",
  },
  {
    value: 15,
    label: "Transmission Tower",
    description: "Transmission Tower",
    color: "#8B0000",
  },
  {
    value: 16,
    label: "Wire-Structure Connector (Insulator)",
    description: "Wire-Structure Connector (Insulator)",
    color: "#FF6347",
  },
  {
    value: 17,
    label: "Bridge Deck",
    description: "Bridge Deck",
    color: "#A52A2A",
  },
  {
    value: 18,
    label: "High Noise",
    description: "High Noise",
    color: "#DC143C",
  },
  { value: 64, label: "Tree", description: "Tree", color: "#006400" },
];

/** Get classification info by value */
export function getClassificationInfo(
  value: number,
): ClassificationCode | undefined {
  if ((value >= 0 && value <= 18) || value === 64) {
    return LAS_CLASSIFICATIONS.find((c) => c.value === value);
  }
  if (value >= 19 && value <= 63) {
    return {
      value,
      label: "Reserved",
      description: "Reserved",
      color: "#696969",
    };
  }
  if (value >= 65 && value <= 255) {
    return {
      value,
      label: "User Definable",
      description: "User Definable",
      color: "#800080",
    };
  }
  return undefined;
}

/** Get available classifications from histogram */
export function getAvailableClassifications(
  histogram?: number[] | null,
): number[] {
  if (!histogram || histogram.length === 0) return [];

  const available: number[] = [];
  histogram.forEach((count, index) => {
    if (count > 0) {
      available.push(index);
    }
  });

  return available;
}
