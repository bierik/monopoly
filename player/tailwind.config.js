module.exports = {
  plugins: [require("daisyui")],
  content: [
    `/components/**/*.{vue,js,ts}`,
    `/pages/**/*.vue`,
    `/layouts/**/*.vue`,
    `/app.vue`,
    "/plugins/**/*.js",
    "nuxt.config.js",
  ],
  daisyui: {
    themes: ["nord"],
    logs: false,
  },
};
