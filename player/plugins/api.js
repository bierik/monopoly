import { createFetch, useFetch } from "@vueuse/core";

export default defineNuxtPlugin(async () => {
  await useFetch("/api/csrf").get();
  const api = createFetch({
    baseUrl: "/api",
    options: {
      beforeFetch({ options }) {
        const { value: csrfToken } = useCookie("csrftoken");
        options.headers = {
          ...options.headers,
          "X-CSRFToken": csrfToken,
        };
        return { options };
      },
    },
  });

  return {
    provide: {
      api,
    },
  };
});
