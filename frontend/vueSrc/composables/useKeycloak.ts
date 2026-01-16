/**
 * Keycloak authentication composable
 *
 * Provides Keycloak SSO integration with master realm.
 * Usage: const { keycloak, isAuthenticated, login, logout } = useKeycloak()
 *
 * Keycloak is initialized only when needed (lazy loading).
 */

import Keycloak from "keycloak-js";
import { ref, computed } from "vue";

// Lazy initialization - Keycloak instance created only when needed
let keycloak: Keycloak | null = null;

const isInitialized = ref(false);
const isAuthenticated = ref(false);
const userProfile = ref<Keycloak.KeycloakProfile | null>(null);
const token = ref<string | undefined>(undefined);

export function useKeycloak() {
  /**
   * Initialize Keycloak (lazy - only when called)
   */
  async function init() {
    if (isInitialized.value) return;

    // Create Keycloak instance on first init
    if (!keycloak) {
      keycloak = new Keycloak({
        url:
          import.meta.env.VITE_KEYCLOAK_URL || "https://enac-it-sso2.epfl.ch",
        realm: import.meta.env.VITE_KEYCLOAK_REALM || "master",
        clientId: import.meta.env.VITE_KEYCLOAK_CLIENT_ID || "addlidar-web",
      });
    }

    try {
      const authenticated = await keycloak.init({
        onLoad: "check-sso",
        pkceMethod: "S256",
        checkLoginIframe: false,
      });

      isAuthenticated.value = authenticated;
      isInitialized.value = true;

      if (authenticated) {
        token.value = keycloak.token;
        try {
          userProfile.value = await keycloak.loadUserProfile();
        } catch (err) {
          console.warn("Failed to load user profile:", err);
        }
      }

      keycloak.onTokenExpired = () => updateToken();
    } catch (error) {
      console.error("Keycloak initialization error:", error);
      isInitialized.value = true;
    }
  }

  /**
   * Login user (redirects to Keycloak)
   */
  async function login() {
    if (!keycloak) {
      await init();
    }

    try {
      await keycloak!.login({
        redirectUri: window.location.href,
      });

      // After redirect back, update state
      if (keycloak!.authenticated) {
        isAuthenticated.value = true;
        token.value = keycloak!.token;
        try {
          userProfile.value = await keycloak!.loadUserProfile();
        } catch (err) {
          console.warn("Failed to load profile after login:", err);
        }
      }
    } catch (error) {
      console.error("Login error:", error);
    }
  }

  /**
   * Logout user
   */
  async function logout() {
    try {
      await keycloak!.logout({
        redirectUri: window.location.origin,
      });
      isAuthenticated.value = false;
      userProfile.value = null;
      token.value = undefined;
    } catch (error) {
      console.error("Logout error:", error);
    }
  }

  /**
   * Update token (refresh if needed)
   */
  async function updateToken(minValidity = 30) {
    try {
      const refreshed = await keycloak!.updateToken(minValidity);
      if (refreshed) {
        token.value = keycloak!.token;
      }
      return keycloak!.token;
    } catch (error) {
      console.error("Token refresh error:", error);
      isAuthenticated.value = false;
      return null;
    }
  }

  /**
   * Get authorization header for API calls
   */
  const authHeader = computed(() => {
    return token.value ? { Authorization: `Bearer ${token.value}` } : undefined;
  });

  return {
    keycloak,
    isInitialized,
    isAuthenticated,
    userProfile,
    token,
    authHeader,
    init,
    login,
    logout,
    updateToken,
  };
}
