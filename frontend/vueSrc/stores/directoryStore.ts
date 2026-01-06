import { defineStore } from "pinia";
import { computed, ref, watch } from "vue";
import type { PointcloudMetadata } from "@/types/pointcloud";

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

export interface PotreeMetacloudState {
  mission_key: string;
  fp: string;
  output_path: string;
  last_checked: number;
  last_processed: number | null;
  processing_time: number | null;
  processing_status: string;
  error_message: string | null;
  last_checked_time: string;
  metacloud_filename: string | null;
  last_processed_time: string | null;
  detailed_error_message: string | null;
  name: string | null;
  date: string | null;
  extra_attributes: string | null;
}

export const useDirectoryStore = defineStore("directory", () => {
  const directoryData = ref<DirectoryNode[]>([]);
  const isLoading = ref(false);
  const error = ref<string | null>(null);
  const pointcloudMetadata = ref<PointcloudMetadata | null>(null);
  const allMissions = ref<PotreeMetacloudState[]>([]);
  const missionPasswords = ref<Record<string, string>>({});
  const isMissionProtected = ref(false);

  // Load saved passwords from sessionStorage on init
  const savedPasswords = sessionStorage.getItem("mission_passwords");
  if (savedPasswords) {
    try {
      missionPasswords.value = JSON.parse(savedPasswords);
    } catch (e) {
      console.error("Failed to load saved passwords:", e);
    }
  }

  // Computed property for current mission password
  const missionPassword = computed(() => {
    return activeMission.value
      ? missionPasswords.value[activeMission.value]
      : null;
  });

  const isPasswordValid = computed(() => {
    return activeMission.value
      ? Boolean(missionPasswords.value[activeMission.value])
      : false;
  });

  // For same-domain deployment, we can use relative URLs
  const apiBasePath = ref("/api");
  const staticBasePath = ref("/static");

  const missionData = computed<PotreeMetacloudState | null>(() => {
    if (activeMission.value) {
      return getMissionByKey(activeMission.value) || null;
    }
    return null;
  });

  // Configure API paths and set active mission (for single mission view)
  function configurePaths(
    api: string,
    static_path: string,
    missionId?: string,
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

  // Check if mission is password protected
  async function checkMissionProtection(missionKey: string): Promise<boolean> {
    try {
      const response = await fetch(
        `${apiBasePath.value}/sqlite/mission_protection/${missionKey}`,
      );

      if (!response.ok) {
        return false;
      }

      const data = await response.json();
      return data.is_protected === true;
    } catch (err) {
      console.error(
        `Error checking mission protection for ${missionKey}:`,
        err,
      );
      return false;
    }
  }

  // Validate password for protected mission
  async function validatePassword(
    missionKey: string,
    password: string,
  ): Promise<boolean> {
    try {
      const response = await fetch(
        `${apiBasePath.value}/sqlite/mission_protection/${missionKey}/validate`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ password }),
        },
      );

      if (!response.ok) {
        return false;
      }

      const data = await response.json();
      return data.valid === true;
    } catch (err) {
      console.error(`Error validating password for ${missionKey}:`, err);
      return false;
    }
  }

  // Set password for current mission
  function setMissionPassword(password: string | null) {
    if (!activeMission.value) return;

    if (password) {
      missionPasswords.value[activeMission.value] = password;
      // Save to sessionStorage
      sessionStorage.setItem(
        "mission_passwords",
        JSON.stringify(missionPasswords.value),
      );
    } else {
      delete missionPasswords.value[activeMission.value];
      sessionStorage.setItem(
        "mission_passwords",
        JSON.stringify(missionPasswords.value),
      );
    }
  }

  // Clear password for specific mission
  function clearMissionPassword(missionKey?: string) {
    const keyToClear = missionKey || activeMission.value;
    if (!keyToClear) return;

    delete missionPasswords.value[keyToClear];
    sessionStorage.setItem(
      "mission_passwords",
      JSON.stringify(missionPasswords.value),
    );
  }

  // Clear all passwords
  function clearAllPasswords() {
    missionPasswords.value = {};
    sessionStorage.removeItem("mission_passwords");
  }

  // Set the active mission and fetch its data
  async function setActiveMission(missionId: string) {
    activeMission.value = missionId;

    // Check if mission is protected
    isMissionProtected.value = await checkMissionProtection(missionId);

    // If not protected, or we have a password, fetch data
    if (!isMissionProtected.value || missionPasswords.value[missionId]) {
      await fetchMissionData(missionId);
    }
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
          err,
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
      const headers: HeadersInit = {};
      const password = missionPasswords.value[missionName];
      if (password) {
        headers["X-Mission-Password"] = password;
      }

      const response = await fetch(
        `${apiBasePath.value}/sqlite/mission_folders/${missionName}`,
        { headers },
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

  // Fetch list of all available missions
  async function fetchAllMissions() {
    try {
      const response = await fetch(
        `${apiBasePath.value}/sqlite/potree_metacloud_state`,
      );

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const responseData = await response.json();
      // Extract the data array from the response
      allMissions.value = responseData.data;
      return responseData.data;
    } catch (err) {
      console.error("Error fetching missions:", err);
      throw err;
    }
  }

  fetchAllMissions();

  // Helper function to get mission keys only
  function getMissionKeys(): string[] {
    return allMissions.value.map((mission) => mission.mission_key);
  }

  // Helper function to get mission by key
  function getMissionByKey(
    missionKey: string,
  ): PotreeMetacloudState | undefined {
    return allMissions.value.find(
      (mission) => mission.mission_key === missionKey,
    );
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
        `${staticBasePath.value}/Potree/${missionName}/metadata.json`,
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

  // Fetch geojson for a specific poincloud
  async function fetchPointcloudGeojson(missionName: string) {
    try {
      const response = await fetch(
        `${staticBasePath.value}/Footprints/${missionName}.geojson`,
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
            err,
          );
        }
      } else {
        pointcloudMetadata.value = null;
      }
    },
    { immediate: true },
  );

  return {
    directoryData,
    allMissions,
    fetchAllMissions,
    getMissionKeys,
    getMissionByKey,
    pointcloudMetadata,
    isLoading,
    error,
    apiBasePath,
    staticBasePath,
    activeMission,
    missionPassword,
    missionPasswords,
    isMissionProtected,
    isPasswordValid,
    checkMissionProtection,
    validatePassword,
    setMissionPassword,
    clearMissionPassword,
    clearAllPasswords,
    fetchAllDirectoryData,
    fetchPointcloudGeojson,
    fetchMissionData,
    missionData,
    getDownloadUrl,
    configurePaths,
    setActiveMission,
  };
});
