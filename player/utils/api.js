await $fetch("/api/csrf/");

export default $fetch.create({
  baseURL: "/api",
  onRequest({ options }) {
    options.headers.append("X-CSRFToken", toValue(useCookie("csrftoken")));
  },
});
