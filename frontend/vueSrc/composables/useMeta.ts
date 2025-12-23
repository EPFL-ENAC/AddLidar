import { useMeta } from "quasar";

export function useAppMeta(overrides?: {
  title?: string;
  titleTemplate?: (title: string) => string;
  description?: string;
}) {
  const defaultDescription =
    "Interactive platform for exploring and visualizing LiDAR point cloud data from aerial surveys conducted by EPFL's ESO laboratory.";

  useMeta({
    title: overrides?.title || "AddLidar",
    titleTemplate:
      overrides?.titleTemplate || ((title) => `${title} | AddLidar`),
    meta: {
      description: {
        name: "description",
        content: overrides?.description || defaultDescription,
      },
      keywords: {
        name: "keywords",
        content:
          "lidar, point cloud, 3d visualization, potree, aerial survey, geospatial, epfl, eso, enac, it4research",
      },
      equiv: {
        "http-equiv": "Content-Type",
        content: "text/html; charset=UTF-8",
      },
    },
  });
}
