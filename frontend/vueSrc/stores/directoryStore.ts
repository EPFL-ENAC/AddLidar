import { defineStore } from "pinia";
import { ref, watch } from "vue";

export interface DirectoryNode {
  folder_key: string;
  mission_key: string;
  fp: string;
  output_path: string;
  size_kb: number;
  file_count: number;
  last_checked: number;
  last_processed: number | null;
  processing_time: number | null;
  processing_status: string | null;
  error_message: string | null;
}

export const useDirectoryStore = defineStore("directory", () => {
  const directoryData = ref<DirectoryNode[]>([]);
  const isLoading = ref(false);
  const error = ref<string | null>(null);
  const pointcloudMetadata = ref<any>(null);

  // For same-domain deployment, we can use relative URLs
  const apiBasePath = ref("/api");
  const staticBasePath = ref("/static");

  // Configure API paths and set active mission (for single mission view)
  function configurePaths(
    api: string,
    static_path: string,
    missionId?: string
  ) {
    apiBasePath.value = api;
    staticBasePath.value = static_path;

    // If mission ID is provided, set it as the active mission
    if (missionId) {
      setActiveMission(missionId);
    }
  }

  // Current active mission ID (from URL parameter)
  const activeMission = ref<string | null>(null);

  // Set the active mission and fetch its data
  async function setActiveMission(missionId: string) {
    activeMission.value = missionId;
    await fetchMissionData(missionId);
  }

  // Modified to fetch only the active mission's data
  async function fetchAllDirectoryData() {
    // If we have an active mission, just fetch that one
    if (activeMission.value) {
      isLoading.value = true;
      error.value = null;

      try {
        const data = await fetchMissionData(activeMission.value);
        console.info(`Fetched data for mission ${activeMission.value}:`, data);
        directoryData.value = data;
      } catch (err) {
        error.value = err instanceof Error ? err.message : "Unknown error";
        console.error(
          `Error fetching data for mission ${activeMission.value}:`,
          err
        );
      } finally {
        isLoading.value = false;
      }
    } else {
      error.value = "No mission specified";
    }
  }

  // Fetch data for a specific mission
  async function fetchMissionData(missionName: string) {
    try {
      const response = await fetch(
        `${apiBasePath.value}/sqlite/folder_state/${missionName}`
      );

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const { data } = await response.json();
      return data as DirectoryNode[];
    } catch (err) {
      console.error(`Error fetching data for mission ${missionName}:`, err);
      throw err;
    }
  }

  // Get download URL for a path
  function getDownloadUrl(path: string): string {
    const cleanPath = path.startsWith("/") ? path.substring(1) : path;
    const pathWithoutZips = cleanPath.replace("zips/", "");
    console.log(`getDownloadUrl: ${pathWithoutZips}`);
    return `${staticBasePath.value}/${pathWithoutZips}`;
  }

  // Fetch metadata for a specific poincloud
  async function fetchPointcloudMetadata(missionName: string) {
    try {
      const response = await fetch(
        `${staticBasePath.value}/Potree/${missionName}/metadata.json`
      );

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      return await response.json();
    } catch (err) {
      console.error(`Error fetching data for mission ${missionName}:`, err);
      throw err;
    }
  }

  watch(
    () => activeMission.value,
    async (newMission) => {
      if (newMission) {
        try {
          const metadata = await fetchPointcloudMetadata(newMission);
          pointcloudMetadata.value = metadata;
          console.log(`Fetched metadata for mission ${newMission}:`, metadata);
        } catch (err) {
          error.value = err instanceof Error ? err.message : "Unknown error";
          console.error(
            `Error fetching metadata for mission ${newMission}:`,
            err
          );
        }
      } else {
        pointcloudMetadata.value = null;
      }
    },
    { immediate: true }
  );

  return {
    directoryData,
    pointcloudMetadata,
    isLoading,
    error,
    apiBasePath,
    staticBasePath,
    activeMission,
    fetchAllDirectoryData,
    fetchMissionData,
    getDownloadUrl,
    configurePaths,
    setActiveMission,
  };
});
