export default defineNuxtRouteMiddleware(async (from) => {
  if (from.name === "login") {
    return;
  }
  const user = useUserStore();
  try {
    await user.fetch();
  } catch (error) {
    if (error.status === 403) {
      return navigateTo({ name: "login", query: { next: from.fullPath } });
    }
  }
});
