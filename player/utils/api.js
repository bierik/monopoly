await $fetch("/api/v1/csrf");

export default $fetch.create({
  baseURL: "/api/v1",
  onRequest({ options }) {
    options.headers.append("X-CSRFToken", toValue(useCookie("csrftoken")));
  },
});
