import { useLocalStorage } from "@vueuse/core";

export function useDeviceToken() {
  return useLocalStorage("deviceToken", null);
}
