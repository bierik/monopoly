await $fetch("/api/csrf/");

export default $fetch.create({
  baseURL: "/api",
  onRequest({ options }) {
    const deviceToken = toValue(useDeviceToken());
    options.headers = {
      ...options.headers,
      "X-CSRFToken": toValue(useCookie("csrftoken")),
      ...(deviceToken && { "X-Device-Token": deviceToken }),
    };
  },
});
