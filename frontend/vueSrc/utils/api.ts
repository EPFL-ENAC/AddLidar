export type SelectOption = {
  label: string;
  value: string;
};

export const formatOptions: SelectOption[] = [
  { label: "PCD ASCII", value: "pcd-ascii" },
  { label: "LAS v1.4", value: "lasv14" },
];

export const levelOptions: SelectOption[] = [
  { label: "Raw 3D laser vectors", value: "0" },
  { label: "ALS Mounting and Calibration", value: "1" },
  { label: "Refined Trajectory Point Cloud", value: "2" },
  { label: "Geo-referenced Point Cloud", value: "3" },
  { label: "Filtered/Denoised Point Cloud", value: "4" },
  { label: "Basic Classification", value: "5" },
  { label: "DTM/DSM/CHM", value: "6" },
  { label: "Segmented Point Cloud", value: "7" },
];

export const epsgOptions: string[] = ["EPSG:4326", "EPSG:3857", "EPSG:2056"];

export const typeOptions: SelectOption[] = [
  { label: "Trajectory", value: "traj" },
  { label: "Point Cloud", value: "pointcloud" },
  { label: "Metadata", value: "metadata" },
  { label: "DSM", value: "DSM" },
];
