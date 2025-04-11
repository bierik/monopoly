await $fetch("/api/csrf/");

export default $fetch.create({
  baseURL: "/api",
  onRequest({ options }) {
    const deviceToken = toValue(useDeviceToken());
    options.headers.append("X-CSRFToken", toValue(useCookie("csrftoken")));
    if (deviceToken) {
      options.headers.append("X-Device-Token", deviceToken);
    }
  },
});
