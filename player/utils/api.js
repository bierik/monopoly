await $fetch("/api/csrf/");

export default $fetch.create({
  baseURL: "/api",
  onRequest({ options }) {
    options.headers = {
      ...options.headers,
      "X-CSRFToken": toValue(useCookie("csrftoken")),
    };
  },
});
