import type { ParsedAttribute } from "@/stores/pointcloudStore";

/**
 * Determines if an attribute should have a range filter
 */
export function isRangeFilterable(attr: ParsedAttribute): boolean {
  // Must be single-element
  if (attr.numElements !== 1) return false;

  // Must have valid min/max
  if (attr.minValue === null || attr.maxValue === null) return false;

  // Exclude if range is meaningless (min === max)
  if (attr.minValue === attr.maxValue) return false;

  // Only include attributes that Potree viewer can filter
  const lowerName = attr.name.toLowerCase();
  const allowedAttributes = [
    "return number",
    "number of returns",
    "gps-time",
    "gps time",
  ];

  return allowedAttributes.some((allowed) => lowerName.includes(allowed));
}

/**
 * Get all attributes that should have range filters
 */
export function getRangeFilterableAttributes(
  attributes: ParsedAttribute[],
): ParsedAttribute[] {
  return attributes.filter(isRangeFilterable);
}

/**
 * Get display label for an attribute
 */
export function getAttributeLabel(attr: ParsedAttribute): string {
  const name = attr.name;

  // Capitalize first letter of each word
  return name
    .split(" ")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

/**
 * Determine step size for range slider based on attribute type and range
 */
export function getAttributeStep(attr: ParsedAttribute): number {
  // For integer types
  if (
    attr.type === "int8" ||
    attr.type === "uint8" ||
    attr.type === "int16" ||
    attr.type === "uint16" ||
    attr.type === "int32" ||
    attr.type === "uint32"
  ) {
    return 1;
  }

  // For float/double, calculate based on range
  if (attr.minValue !== null && attr.maxValue !== null) {
    const range = attr.maxValue - attr.minValue;
    if (range < 1) return 0.01;
    if (range < 10) return 0.1;
    if (range < 100) return 1;
    return Math.pow(10, Math.floor(Math.log10(range)) - 2);
  }

  return 0.1;
}

/**
 * Format value for display
 */
export function formatAttributeValue(
  value: number,
  attr: ParsedAttribute,
): string {
  // Handle undefined/null values
  if (value === undefined || value === null || isNaN(value)) {
    return "N/A";
  }

  // For integer types, show no decimals
  if (
    attr.type === "int8" ||
    attr.type === "uint8" ||
    attr.type === "int16" ||
    attr.type === "uint16" ||
    attr.type === "int32" ||
    attr.type === "uint32"
  ) {
    return value.toFixed(0);
  }

  // For floats, determine precision based on range
  if (attr.minValue !== null && attr.maxValue !== null) {
    const range = attr.maxValue - attr.minValue;
    if (range < 1) return value.toFixed(3);
    if (range < 10) return value.toFixed(2);
    if (range < 100) return value.toFixed(1);
  }

  return value.toFixed(2);
}
