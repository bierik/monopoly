await $fetch("/api/v1/csrf");

export default $fetch.create({
  baseURL: "/api/v1",
  onRequest({ options }) {
    const deviceToken = toValue(useDeviceToken());
    options.headers.append("X-CSRFToken", toValue(useCookie("csrftoken")));
    if (deviceToken) {
      options.headers.append("X-Device-Token", deviceToken);
    }
  },
});
